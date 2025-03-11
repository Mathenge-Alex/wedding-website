from django.shortcuts import render, redirect, get_object_or_404
from .models import Image, Contact, Discount
from .forms import ImageForm, ContactForm
from django.core.mail import send_mail
from django.contrib import messages
import os
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone


def home(request):
    return render(request, 'images/home.html')

def gallery(request):

    category_order = ['medium', 'long', 'tall']
    images = {category: [] for category in category_order}
    list_images = Image.objects.all()
    for category in category_order:
        images[category] = Image.objects.filter(category=category)

    return render(request, 'images/gallery.html', {'images': images, 'list_images': list_images})


# Improvement of previous Image Detail. Loops Across images and categories

def image_detail(request, pk):
    category_order = ['medium', 'long', 'tall']
    image = get_object_or_404(Image, pk=pk)
    nav_mode = request.GET.get('nav', 'category')  # Default to 'category' navigation

    if nav_mode == 'category':
        # Current category images
        images_in_category = Image.objects.filter(category=image.category).order_by('id')
        all_images = {category: Image.objects.filter(category=category).order_by('id') for category in category_order}
    else:  # nav_mode == 'all'
        all_images_ordered = []
        for category in category_order:
            all_images_ordered.extend(Image.objects.filter(category=category).order_by('id'))
        all_images = {'all': all_images_ordered}

    # Finding next and previous images
    def find_next_prev(images_dict):
        for key, images in images_dict.items():
            image_ids = list(images.values_list('id', flat=True))
            if image.id in image_ids:
                current_idx = image_ids.index(image.id)
                num_images = len(image_ids)
                prev_idx = (current_idx - 1) % num_images
                next_idx = (current_idx + 1) % num_images
                prev_image = images.get(id=image_ids[prev_idx])
                next_image = images.get(id=image_ids[next_idx])
                return prev_image, next_image
        return None, None

    prev_image, next_image = find_next_prev(all_images if nav_mode == 'all' else {image.category: images_in_category})

    # Navigation across categories for 'category' navigation mode
    if nav_mode == 'category' and (prev_image is None or next_image is None):
        current_category_idx = category_order.index(image.category)
        if prev_image is None:  # At the first image of the category
            # Go to the last image of the previous category
            previous_category = category_order[(current_category_idx - 1) % len(category_order)]
            prev_image = Image.objects.filter(category=previous_category).order_by('id').last()
        if next_image is None:  # At the last image of the category
            # Go to the first image of the next category
            next_category = category_order[(current_category_idx + 1) % len(category_order)]
            next_image = Image.objects.filter(category=next_category).order_by('id').first()

    context = {
        'image': image,
        'prev_image_id': prev_image.id if prev_image else None,
        'next_image_id': next_image.id if next_image else None,
        'nav_mode': nav_mode
    }
    return render(request, 'images/image_detail.html', context)


# Contact View
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact form submission to the database
            contact = Contact.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                wedding_venue=form.cleaned_data['wedding_venue'],
                phone_number=form.cleaned_data['phone_number'],
                message=form.cleaned_data['message'],
            )

            # Send an email with the contact form information
            send_mail(
                subject=f"Wedding Painting Request from {contact.first_name} {contact.last_name}: {contact.wedding_venue}",
                message=contact.message + f"\n\nClient's Name: {contact.first_name} {contact.last_name} \nWedding Venue: {contact.wedding_venue} \nContact Email Address: {contact.email} \nPhone Number: {contact.phone_number}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],  # Add your email or any other recipient
                fail_silently=False,
            )
            messages.success(request, 'Your wedding request has been received, Vesna will reach out to you ASAP!')

            send_mail(
                subject="We have received your request",
                message=f"Hello {contact.first_name}, \n\nThank you for reaching out. \n\nVesna has received your request and will get back to you shortly.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[contact.email],
                fail_silently=False,
            )

            form = ContactForm()
    else:
        form = ContactForm()

    return render(request, 'images/contact.html', {'form': form})

# About Artist
def about_artist(request):

    return render(request, 'images/about_artist.html')

# Prices
def pricing(request):
    current_time = timezone.now()
    active_discounts = Discount.objects.filter(
        active=True,
        start_date__lte=current_time,
        end_date__gte=current_time
    )
    context = {
        'active_discounts': active_discounts,
    }
    return render(request, 'images/prices.html', context)

#
def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery')
    else:
        form = ImageForm()
    return render(request, 'images/upload_image.html', {'form': form})


#Robots Read from text file

def robots_txt(request):
    robots_path = os.path.join(settings.BASE_DIR, 'robots.txt')
    with open(robots_path, 'r') as f:
        text = f.read()
    return HttpResponse(text, content_type='text/plain')