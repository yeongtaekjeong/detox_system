from django.shortcuts import render, redirect

def survey_project(request):
    return render(request, 'detoxapp/question/survey_project.html',{})