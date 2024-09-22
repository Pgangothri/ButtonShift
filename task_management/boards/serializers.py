from rest_framework import serializers
from .models import WorkBoard, Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assigned_to', 'assigned_to_id', 'created_at', 'updated_at']


class WorkBoardSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = WorkBoard
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'tasks']

    def create(self, validated_data):
        user = self.context['request'].user
        work_board = WorkBoard.objects.create(owner=user, **validated_data)
        return work_board
