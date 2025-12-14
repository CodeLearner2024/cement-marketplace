from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse

from .models import Product, Category
from .forms import ProductForm
