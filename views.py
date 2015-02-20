from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context, Template
from django.contrib.auth.decorators import login_required
from chef.models import *
from chef.forms import *
from turpial_push.models import *
from datetime import datetime as date2
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
import datetime 
from django.db.models import Count
import hashlib
import unicodedata
import qsstats
import dateutil
from datetime import date
import re
import Image
from easy_thumbnails.files import get_thumbnailer
from django.core.exceptions import ObjectDoesNotExist
from gcm import GCM
from apns import APNs, Payload
import time


def push_notifications(request):
  mensajes = NewMessages.objects.filter(pushed=False)
  print mensajes
  fecha = str(date.today())
  print fecha
  hora = str(datetime.datetime.now().hour)
  print "aqui viene la hora"
  print hora
  for mensaje in mensajes:
    print "la fecha a la que voy a enviar"
    print mensaje.date
    print "la fecha de hoy"
    titulo = str(mensaje.date_statistics)
    if mensaje.date == fecha:
      print "la hora es" + hora
      print "la hora de mensaje es" + mensaje.hour_send
      if int(mensaje.hour_send) <= int(hora):
        print "Hoyyyyy :)"
        usuarios = mensaje.name_user.values_list()
        for usuario in usuarios:
          print "push"
          push_textmessages(usuario[0],"Scheduled delivery for " + titulo)
        mensaje.pushed = True
        mensajesmany = NewMessagesMany.objects.filter(message=mensaje)
        for mensajeaux in mensajesmany:
          mensajeaux.pushed = True
          mensajeaux.save()
        mensaje.save()
        
  return HttpResponseRedirect('/')# Create your views here.

def push_textmessages(id_client,title):
  print title
  usuario = Clients.objects.get(id=id_client)
  phones = Phone.objects.filter(client = usuario)
  for phone in phones:
    if phone.os == "Android":
      print "android"
      gcm = GCM('AIzaSyAwe-R232TtAcT7Yiary4cgcz0Blo56m-Q')
      data = {'message': title}
      reg_id = phone.reg_id
      gcm.plaintext_request(registration_id=reg_id, data=data)
    else:
      print "ios"
      apns = APNs(use_sandbox=False, cert_file='/home/leonardo/turpial/recipe/repo/kooshi/recipe/turpial_push/cert/apns-dev-cert.pem', key_file='/home/leonardo/turpial/recipe/repo/kooshi/recipe/turpial_push/cert/apns-dev-key-noenc.pem')
      token_hex = phone.reg_id
      number = MessagesReceived.objects.filter(user=usuario,read=False,income=True).count()
      payload = Payload(alert=title, sound="default", badge=number)
      try:
        apns.gateway_server.send_notification(token_hex, payload)
      except:
        pass
  return True
