from rest_framework import routers
from room.views import BoardViewSet


router = routers.DefaultRouter()
router.register(r'board', BoardViewSet)
