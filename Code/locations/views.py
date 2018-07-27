from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,\
    RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from locations.models import Bookmark, Comment, Note, Like
from locations.serializers import BookmarkSerializer, NoteSerializer,\
    CommentSerializer, CommentSerializerWithLikes, BookmarkLinkSerializer
from rest_framework.decorators import action
from django.db.models.aggregates import Count

# Create your views here.


class SimpleHelloWorld(View):
    """
    View that returns Hello World
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h1>Hello world</h1>')


class SimpleHelloPerson(View):
    """
    View that returns Hello $person parameter
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h1>Hello {}</h1>'.format(kwargs['name']))


class TemplateHelloPerson(TemplateView):
    """
    View that uses template to return Hello $person parameter
    """
    template_name = 'locations/hello.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = self.kwargs['name']
        return context


class SimpleHelloWorldAPI(View):
    """
    View that returns a name parameter in a JSON response
    """
    def get(self, request, *args, **kwargs):
        if kwargs['name'].lower() != 'fred':
            return JsonResponse(
                {
                    'description': 'This endpoint welcomes the user',
                    'welcome': 'Hello {}'.format(kwargs['name'])
                },
                status=200
            )
        else:
            return JsonResponse(
                {
                    'description': 'This demonstrates an error',
                    'error': '{} is not an authorised user'.format(
                        kwargs['name']
                    )
                },
                status=403
            )


class BookmarkListView(APIView):
    """
    List all bookmarks, or create a new bookmark
    """
    def get(self, request, format=None):
        bookmarks = Bookmark.objects.all()
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BookmarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookmarkDetailView(APIView):
    """
    Retrieve, update or delete a bookmark.
    """
    def get_object(self, pk):
        try:
            return Bookmark.objects.get(pk=pk)
        except Bookmark.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        bookmark = self.get_object(pk)
        serializer = BookmarkSerializer(bookmark)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        bookmark = self.get_object(pk)
        serializer = BookmarkSerializer(bookmark, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bookmark = self.get_object(pk)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkList(ListCreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer


class BookmarkDetail(RetrieveUpdateDestroyAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer


class BookmarkViewSet(ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkLinkSerializer

    def get_queryset(self):
        return Bookmark.objects.annotate(
            num_likes=Count('likes')
        )

    @action(methods=['post'], detail=True)
    def add_like(self, request, pk=None):
        object = self.get_object()
        like = Like()
        like.bookmark = object
        like.save()
        return Response(
            {'status': 'bookmark like set'},
            status=status.HTTP_201_CREATED
        )

class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerWithLikes

    def get_queryset(self):
        return Comment.objects.annotate(
            num_likes=Count('likes')
        )

    @action(methods=['post'], detail=True)
    def add_like(self, request, pk=None):
        object = self.get_object()
        like = Like()
        like.comment = object
        like.save()
        return Response(
            {'status': 'comment like set'},
            status=status.HTTP_201_CREATED
        )
