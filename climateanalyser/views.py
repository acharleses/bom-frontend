from django.utils.dateformat import format
from django.template.loader import get_template
from django.shortcuts import render
from django.template import RequestContext,loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import *
from models import *
from django.contrib import messages
from django.http import StreamingHttpResponse
from django.conf import settings

def index(request):
   #Default page
   t = loader.get_template('index.html')
   context = RequestContext(request, {})
   html = t.render(context)
   return HttpResponse(html)

def datafiles(request): 
   return render(request, 'datafiles.html', { 'datafiles' : 
         DataFile.objects.filter() })

def create_datafile(request):

   if (request.user.is_authenticated() == False):
      messages.error(request, 'You must login to view that page.')
      return HttpResponseRedirect('/login')

   if request.method == 'POST':

      form = DataFileForm(request.POST)

      if form.is_valid():

         form.save()

         messages.success(request, 'Data File successfully created!')
         return HttpResponseRedirect('/datafiles')
      
   else:
      form = DataFileForm()

   return render(request, 'create_datafile.html', { 'form' : form })

def create_computation(request, computation_pk=None): 
   #Form for creating new computation

   if computation_pk:
      computation = Computation.objects.get(pk=computation_pk)
   else:
      computation = Computation()
   
   ComputationFormSet = inlineformset_factory(Computation, ComputationData,
         form=ComputationDataForm,extra=2)
  
   if request.method == 'POST':
      form = ComputationForm(request.POST,instance=computation)
      formset = ComputationFormSet(request.POST,instance=computation)

      if form.is_valid() and formset.is_valid():
         form.save()
         formset.save()
         messages.success(request, 'Computation successfully created!')
         return HttpResponseRedirect('/computations')

   else:
      form = ComputationForm(initial={ 'created_by': request.user },instance=computation)
      formset = ComputationFormSet(instance=computation)

   return render(request, 'create_computation.html', 
         { 'form' : form, 'formset' : formset, })

def computation(request):
   #display single computation
   computation = Computation.objects.get(id=request.GET.get('id'))

   return render(request, 'computation.html', {'computation': computation})

def computations(request):
   #View list of computations in the system

   template_params = {}

   #Filter for current user
   if request.GET.get('show_mine'):
      user = request.user
      template_params['computations'] = Computation.objects.filter(
            created_by=user)
      template_params['show_mine'] = True;
   else:
      template_params['computations'] = Computation.objects.filter()
      template_params['show_mine'] = False;

   return render(request, 'computations.html', template_params)

def load_cache(request):

   file = request.GET.get('file')

   if file:
      full_path = settings.CACHE_DIR + file
      response = StreamingHttpResponse(open(full_path))
      return response

   return HttpResponse('')
