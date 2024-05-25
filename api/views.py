import base64
from io import BytesIO
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse

import qrcode
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth.models import User
from core.models import Conversation, Message
from core.serializers import ConversationSerializer, MessageSerializer, UserSerializer

# ######################################### #
#               users methods               #
# ######################################### #
class UserApiView:
    @api_view(['POST'])
    def register(request):
        data = request.data
        try:
            user = User.objects.create_user(username=data.get('username'), email=data.get('email'), password=data.get('password'))
            serializer = UserSerializer(instance=user, data=data)
            if serializer.is_valid():
                user.save()
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'detail': str(serializer.errors)}, status=status.HTTP_206_PARTIAL_CONTENT)
        except IntegrityError:
            return JsonResponse({'detail': f'This user already exist'}, status=status.HTTP_302_FOUND)
        except Exception as error:
            return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['POST'])
    def auth_username(request):
        data = request.data
        try:
            user = authenticate(username=data.get('username'), password=data.get('password'))
            if user is None:
                userM = User.objects.get(email=data.get('username'))
                serializers = UserSerializer(userM, many=False)
                if userM is None:
                    return JsonResponse({'detail': f'This user not found'}, status=status.HTTP_404_NOT_FOUND)
                else :
                    if userM.check_password(data.get('password')):
                        refreshM = RefreshToken.for_user(userM)
                        return JsonResponse({'user': serializers.data, 'refresh': str(refreshM), 'token': str(refreshM.access_token),}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({'detail': f'Invalid password'}, status=status.HTTP_404_NOT_FOUND)
            else:
                userS = User.objects.get(username=data.get('username'))
                serializers = UserSerializer(userS, many=False)
                refresh = RefreshToken.for_user(user)
                return JsonResponse({'user': serializers.data, 'refresh': str(refresh), 'token': str(refresh.access_token),}, status=status.HTTP_200_OK)
        except Exception as error :
            return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['POST', 'GET'])
    @permission_classes([IsAuthenticated]) 
    def auth_logout(request):
        jwtAuthentication = JWTAuthentication()
        try: 
            gtoken = jwtAuthentication.get_header(request)
            print(gtoken)
            if gtoken is None:
                return JsonResponse({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
            
            # raw_token = jwtAuthentication.get_raw_token(gtoken)
            # validated_token = jwtAuthentication.get_validated_token(raw_token)
            decoded_token = AccessToken(gtoken)
            user_id = decoded_token['user_id']
            user = User.objects.get(id=user_id)
            
            token = RefreshToken.for_user(user)
            token.blacklist()
            return JsonResponse({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as error:
            return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    def auth_validated(request):
        # print(request.data)
        return HttpResponse(request.data)


# ######################################### #
#               chats methods               #
# ######################################### #
class ConversationApiView:
    @api_view(['GET', 'POST'])
    @permission_classes([IsAuthenticated])
    def get(request):
        if request.method == 'GET':
            try:
                chats = Conversation.objects.all().filter(user=request.user.id)
                serializers = ConversationSerializer(chats, many=True)
                return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)
            except Exception as error:
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'POST':
            dataR = request.data
            user = request.user
            try :
                conversation = Conversation(name=dataR.get('name'), agent=dataR.get('agent'), user=user)
                serializers = ConversationSerializer(conversation)
                conversation.save()
                return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)
            except Exception as error:
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    @api_view(['PATCH', 'DELETE'])
    @permission_classes([IsAuthenticated])
    def rud(request, id):
        if request.method == 'PATCH':
            try:
                chats = Conversation.objects.get(id=id)
                chats.name = request.data.get('name')
                if request.data.get('name') is not None:
                    chats.agent = request.data.get('agent')
                chats.save()
                serializers = ConversationSerializer(chats, many=False)
                return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)
            except Exception as error:
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.method == 'DELETE':
            try:
                chats = Conversation.objects.get(id=id)
                chats.delete()
                return JsonResponse({'detail': f'Chat {id} are deleted'}, status=status.HTTP_200_OK)
            except Exception as error:
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        

# ######################################### #
#             messages methods              #
# ######################################### #
class MessageApiView:
    @api_view(['GET', 'POST'])
    @permission_classes([IsAuthenticated])
    def send(request):
        if request.method == 'POST':
            data = request.data
            user = request.user
            try :
                conversation = data.get('conversation') 
                if conversation is None:
                    conversation_generated = Conversation(name=data.get('message'), agent='CHATGPT', user=user)
                    conversation_generated.save()
                    conversation = conversation_generated.id
                cvst = Conversation.objects.get(id=conversation)
                message = Message(image=data.get('image'), audio=data.get('audio'), message=data.get('message'),  from_agent=data.get('from_agent'), conversation=cvst)
                serializers = MessageSerializer(message)
                message.save()
                return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)
            except Exception as error:
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'GET':
            data = request.data
            try :
                conversations = Message.objects.filter(conversation=data.get('conversation'))
                serializers = MessageSerializer(conversations, many=True)
                return JsonResponse(serializers.data, status=status.HTTP_200_OK, safe=False)
            except Exception as error:
                print(error)
                return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
            
        
    @api_view(['DELETE'])
    @permission_classes([IsAuthenticated])
    def delete(request, id):
        try:
            message = Message.objects.get(id=id)
            message.delete()
            return JsonResponse({'detail': f'The message {id} are deleted'}, status=status.HTTP_200_OK, safe=False)
        except Exception as error:
            return JsonResponse({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_qr_code(url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=5,
        )
        qr.add_data(url)
        path = ('./static/image')
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        temp = BytesIO()
        img.save(path, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        return qr_img