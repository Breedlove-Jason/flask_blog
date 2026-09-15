import os
import re
import tempfile
os.environ['SECRET_KEY'] = 'test-only-key-not-for-production'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
import pytest
from app import app, db, User, BlogPost, Comment

@pytest.fixture
def client():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, ADMIN_USER_ID=0)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register(client, email='reader@example.com'):
    return client.post('/register', data=dict(name='Reader',email=email,password='long-test-password'), follow_redirects=True)

def post_data():
    return dict(title='Test note',subtitle='A useful experiment',body='<p>Hello</p>',img_url='https://example.com/image.jpg')

def admin(client):
    register(client)
    app.config['ADMIN_USER_ID'] = User.query.first().id

def test_register_login_and_case_normalization(client):
    assert register(client, 'Reader@example.com').status_code == 200
    assert User.query.first().email == 'reader@example.com'
    client.post('/logout')
    r=client.post('/login',data=dict(email='READER@example.com',password='long-test-password'))
    assert r.status_code == 302
    assert User.query.first().password != 'long-test-password'

def test_second_registrant_never_becomes_admin(client):
    register(client)
    client.post('/logout')
    register(client,'second@example.com')
    assert client.post('/new-post',data=post_data()).status_code == 403
    assert BlogPost.query.count() == 0

def test_publish_edit_comment_and_delete(client):
    admin(client)
    assert client.post('/new-post',data=post_data()).status_code == 302
    post=BlogPost.query.first()
    assert post.author_id == User.query.first().id
    assert client.get('/post/'+str(post.id)).status_code == 200
    edited=post_data();edited['title']='Edited'
    assert client.post('/edit-post/'+str(post.id),data=edited).status_code == 302
    assert db.session.get(BlogPost,post.id).title == 'Edited'
    client.post('/post/'+str(post.id),data=dict(comment='<script>alert(1)</script>',submit_comment='Submit'))
    html=client.get('/post/'+str(post.id)).get_data(as_text=True)
    assert '&lt;script&gt;' in html
    assert client.get('/delete/'+str(post.id)).status_code == 405
    assert client.post('/delete/'+str(post.id)).status_code == 302
    assert Comment.query.count() == 0

def test_unknown_post_and_public_pages(client):
    assert client.get('/post/999').status_code == 404
    for path in ['/','/about','/contact','/register','/login','/health']:
        assert client.get(path).status_code == 200

def test_html_filter_and_csrf(client):
    admin(client)
    data=post_data();data['body']='<script>alert(1)</script><a href="javascript:alert(1)">bad</a><strong>good</strong>'
    client.post('/new-post',data=data)
    html=client.get('/post/1').get_data(as_text=True)
    assert '<script>' not in html and 'javascript:' not in html and '<strong>good</strong>' in html
    app.config['WTF_CSRF_ENABLED']=True
    assert client.post('/delete/1').status_code == 400
    html=client.get('/post/1').get_data(as_text=True)
    token=re.search(r'name="csrf_token" value="([^"]+)"',html).group(1)
    assert client.post('/delete/1',data={'csrf_token':token}).status_code == 302

def test_duplicate_title_does_not_crash(client):
    admin(client)
    client.post('/new-post',data=post_data())
    assert client.post('/new-post',data=post_data()).status_code == 200
    assert BlogPost.query.count() == 1

def test_sample_articles_and_home_photo(client):
    html=client.get('/').get_data(as_text=True)
    assert 'rebuilding-pacman' in html and 'SAMPLE ARTICLE' in html
    for slug in ['rebuilding-pacman','reuters-document-similarity','building-field-notes']:
        assert client.get('/notes/'+slug).status_code == 200
    assert client.get('/notes/missing').status_code == 404
    assert b'blogimagetools.jpg' in client.get('/static/css/field-notes.css').data

def test_editor_requires_explicit_access(client):
    register(client)
    assert client.get('/editor').status_code == 403
    app.config['ADMIN_USER_ID']=User.query.first().id
    assert client.get('/editor').status_code == 200
