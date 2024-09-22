from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import WorkBoard, Task
from .serializers import WorkBoardSerializer, TaskSerializer

# Custom permission class to ensure only the owner can modify the object
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner
        return obj.owner == request.user


# ViewSet for WorkBoard
class WorkBoardViewSet(viewsets.ModelViewSet):
    serializer_class = WorkBoardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return WorkBoard.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Custom action to add a task to a specific work board
    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        work_board = self.get_object()
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(work_board=work_board)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ViewSet for Task
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(work_board__owner=self.request.user)

    # Custom action to update the status of a task
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        
        # Validate if the status exists in Task.STATUS_CHOICES
        if not new_status:
            return Response({'status': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({'status': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = new_status
        task.save()
        return Response({'status': 'Status updated'}, status=status.HTTP_200_OK)

    # Custom action to assign a user to a task
    @action(detail=True, methods=['patch'])
    def assign_user(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')

        # Validate if the user ID is provided
        if not user_id:
            return Response({'status': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            task.assigned_to = user
            task.save()
            return Response({'status': 'User assigned'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'status': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
