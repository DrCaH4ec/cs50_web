from django.http import HttpResponse
from django.shortcuts import render
from . import util
from django import forms
from markdown2 import Markdown
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def is_entry_exist(entry_name):
    
    list = util.list_entries()
    
    for entry in list:
        if entry_name.lower() == entry.lower():
            markdowner = Markdown()
            print("Entry name: ", entry_name)
            page_converted = markdowner.convert(util.get_entry(entry))
            return page_converted

    return None

def show_entry(request, title):
    return render(request, "encyclopedia/show_entry.html", {
        "entry": is_entry_exist(title),
        "entry_name": title
    })
    
    
def search_entry(request):
    
    list = []
    
    if request.method == "POST":
        name = request.POST.get("q")
    
        entries = util.list_entries()
        
        if is_entry_exist(name):
            return render(request, "encyclopedia/show_entry.html", {
                "entry": is_entry_exist(name),
                "entry_name": name
            })
        
        for i in entries:
            if name.lower() in i.lower():
                list.append(i)
    
    return render(request, "encyclopedia/search_results.html", {
        "entries": list
    })

def add_entry(request):
    
    if request.method == "POST":
        
        content = request.POST.get("content")
        
        title = request.POST.get("title")
    
        if title in util.list_entries():
            return render(request, "encyclopedia/add_entry.html", {
                "msg": "Title must be unique!",
                "title" : title,
                "content": content
            })
    
        util.save_entry(title, content)
    
        return HttpResponseRedirect(reverse("show_entry", args=[title]))
    
    return render(request, "encyclopedia/add_entry.html", {
        "msg": "",
        "title" : "",
        "content": ""
    })


def edit_entry(request, title):
    
    content = util.get_entry(title)
    
    if request.method == "POST":
        
        content = request.POST.get("content")
        util.save_entry(title, content)
    
        return HttpResponseRedirect(reverse("show_entry", args=[title]))
    
    return render(request, "encyclopedia/edit_entry.html", {
        "title" : title,
        "content": content
    })
    
def random_page(request):
    list = util.list_entries()
    random_title = random.choice(list)
    
    return HttpResponseRedirect(reverse("show_entry", args=[random_title]))