from django.test import SimpleTestCase, TestCase
from django.test.client import RequestFactory
from django.urls.base import reverse
from django.test import tag
from .views import TemplateHelloPerson, BookmarkViewSet
from rest_framework.test import APIClient
from locations.models import Bookmark, Note, Comment, Like
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from django.db.models.aggregates import Count
from rest_framework.test import APIRequestFactory
from unittest.mock import patch, Mock
from rest_framework.response import Response
from rest_framework import status

# Create your tests here.


class ITTest_TemplateHelloPerson(SimpleTestCase):
    @tag('integration_test')
    def test_render(self):
        response = self.client.get(
            reverse('hello-view3', kwargs={'name': 'Allan'}), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.url_name, 'hello-view3')
        self.assertContains(response, b'<title>Hello Allan</title>')
        self.assertContains(
            response, b'<p>There are 5 characters in your name</p>'
        )
        self.assertContains(
            response, b'you have not won'
        )


class UTTest_TemplateHelloPerson(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('/fake-path')
        self.view = TemplateHelloPerson()
        self.view = setup_view_test(self.view, self.request)

    @tag('unit_test')
    def test_class_attributes(self):
        self.assertEqual(self.view.template_name, 'locations/hello.html')

    @tag('unit_test')
    def test_get_context_data(self):
        self.view.kwargs['name'] = 'Fred'
        context = self.view.get_context_data()
        self.assertEqual(context['name'], 'Fred')


def setup_view_test(view, request, *args, **kwargs):
    """
    Mimic as_view() returned callable, but returns view instance.

    args and kwargs are the same you would pass to ``reverse()``
    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view


class Test_BookmarkViewset(TestCase):
    def setUp(self):
        super().setUp()
        bookmark1 = Bookmark(link="http://www.google.com/")
        bookmark1.save()
        bookmark2 = Bookmark(link="http://www.cnn.com/")
        bookmark2.save()
        bookmark3 = Bookmark(link="http://www.bbc.co.uk/")
        bookmark3.save()
        note = Note(text="This is a note", bookmark=bookmark2)
        note.save()
        comment = Comment(bookmark=bookmark3, text="This is a comment")
        comment.save()
        like1 = Like(bookmark=bookmark1)
        like1.save()
        like2 = Like(comment=comment)
        like2.save()

    @tag('integration_test')
    def test_get(self):
        client = APIClient()
        result = client.get('/locations/bookmarks/')
        stream = BytesIO(result.content)
        data = JSONParser().parse(stream)
        self.assertEqual(len(data), 6)

    @tag('integration_test')
    def test_add_like(self):
        bookmark = Bookmark.objects.annotate(num_likes=Count('likes')).get(id=6)
        self.assertEqual(bookmark.num_likes, 0)
        client = APIClient()
        result = client.post('/locations/bookmarks/6/add_like/')
        bookmark = Bookmark.objects.annotate(num_likes=Count('likes')).get(id=6)
        self.assertEqual(bookmark.num_likes, 1)
        result = client.post('/locations/bookmarks/6/add_like/')
        bookmark = Bookmark.objects.annotate(num_likes=Count('likes')).get(id=6)
        self.assertEqual(bookmark.num_likes, 2)

    @tag('unit_test')
    @patch('locations.views.Response')
    @patch('locations.views.BookmarkViewSet.get_object')
    @patch('locations.views.Like')
    def test_add_like(self, l_patch, go_patch, r_patch):
        factory = APIRequestFactory()
        request = factory.post(
            '/locations/bookmarks/6/add_like/', {}
        )
        view = BookmarkViewSet()
        result = view.add_like(request)
        self.assertEqual(go_patch.call_count, 1)
        self.assertEqual(l_patch.call_count, 1)
        self.assertEqual(l_patch.return_value.bookmark, go_patch.return_value)
        self.assertEqual(l_patch.return_value.save.call_count, 1)
        self.assertEqual(r_patch.call_count, 1)
        self.assertEqual(r_patch.call_args[0], ({'status': 'bookmark like set'},))
        self.assertEqual(r_patch.call_args[1], {'status': status.HTTP_201_CREATED})
        self.assertEqual(result, r_patch.return_value)
