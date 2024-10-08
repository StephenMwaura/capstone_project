from django.shortcuts import render
from .models import Movie , Moviereview, Comment
from rest_framework.permissions import IsAuthenticated , AllowAny,IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
# Create your views here.
from rest_framework import viewsets
from .serializers import MoviereviewSerializer,MovieSerializer,UserSerializer,CommentSerializer,ProfileSerializer, UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.db import models # allows the MostlikedReviewviewset to count the most liked review
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsAuthorOrReadOnly

class UserRegistrationView(generics.CreateAPIView): #Provides a post method for handling registration
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] # any person can register

    
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data) # get the serializer instance from the request object and return it as a serializer
        
        if serializer.is_valid():
            serializer.save()
            # Create a token for the newly created user
            token, created = Token.objects.get_or_create(user=serializer.instance) # creates a token for the newly created user
            return Response({
                "user": serializer.data,
                "token": token.key,
            }, status=status.HTTP_201_CREATED)
        
        # Return error response if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserListViewSet(viewsets.ModelViewSet): # this allows the admin to see the list of users
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] # access only for admin users


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

class MovieReviewViewSet(viewsets.ModelViewSet):
    queryset = Moviereview.objects.all()
    serializer_class = MoviereviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['movie__title'] # allows users to search movie review by movie titles
    filterset_fields = ['movie__title','rating'] # allowers filtering by movie title and rating
    ordering_fields = ['rating'] # allows users to sort movie reviews by rating 

  

    def perform_create(self , serializer): # creating a moviereview
        serializer.save(user=self.request.user) # save the movie review 

    @action(detail=True,methods=['post'],permission_classes=[IsAuthenticated])
    def like(self, request,pk=None): # like a movie review 
        review = self.get_object() # get the movie review
        user = request.user

        if user in review.likes.all(): # check if user the user has already liked this review
            review.likes.remove(user) # if user has already liked this review then the user will be removed
            return Response ({'status': 'review unliked'},status=status.HTTP_200_OK)
        else:
            review.likes.add(user) # if the user has not liked this review the user is added to the list
            return  Response({'status': 'liked'},status=status.HTTP_200_OK)
        
    
class ProfileView(generics.RetrieveUpdateAPIView): # allows users to retrieve their profile information and can update using the put method
    queryset = User.objects.all() # get all the users
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_object(self):
        return self.request.user.profile # gets the current authenticated user
    

    

class MostlikedReviewViewSet(viewsets.ReadOnlyModelViewSet): # allows retrieving the most liked review
    serializer_class = MoviereviewSerializer

    def get_queryset(self): # gets the most liked review
        return Moviereview.objects.annotate(likes_count=models.Count('likes')).order_by('-likes_count')[:5] # gets the 5 most liked reviews
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer): # creating a comment
        serializer.save(user=self.request.user)

