from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from django.shortcuts import get_object_or_404

def home(request):
	# Display records logic
	records = Record.objects.all()
	records = Record.objects.annotate(quant_int=Cast('quant', IntegerField()))

	query = request.GET.get('q')
	sort_by = request.GET.get('sort', 'id')  # Default sort by 'id'

	if query:
		records = records.filter(name__icontains=query)
		message = f"Showing results for '{query}'"
	else:
		message = "Showing all records"

	if sort_by == 'quant':
		records = records.annotate(quant_int=Cast('quant', IntegerField())).order_by('quant_int')
	elif sort_by == 'serial_num':
		records = records.annotate(serial_num_int=Cast('serial_num', IntegerField())).order_by('serial_num_int')
	else:
		records = records.order_by(sort_by)

	# Login logic
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, "Successfully Logged In!")
			return redirect('home')
		else:
			messages.error(request, "Error Logging In...")

	# Low stock alert logic
	if request.user.is_authenticated:
		low_stock_items = records.filter(quant_int__lte=5)
		if low_stock_items.exists():
			messages.warning(request, "Some items are low in stock. Please restock them soon.")

	return render(request, 'home.html', {'records': records, 'message': message, 'query': query})




def logout_user(request):
	logout(request)
	messages.success(request, "Successfully Logged Out!")
	return redirect('home')

def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and Login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username = username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered Your Account!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})


def item_record(request, pk):
	if request.user.is_authenticated:
		# Look Up Record
		item_record = Record.objects.get(id=pk)
		return render(request, 'record.html', {'item_record':item_record})

	else:
		messages.success(request, "You Must Be Logged In To View This Page")
		return redirect('home')

def delete_record(request, pk):
	if request.user.is_authenticated:
		record = get_object_or_404(Record, id=pk)
		# Create an AuditLog entry before deleting the record
		AuditLog.objects.create(
			action='deleted',
			details=f"Record {record.name} was deleted.",
			user=request.user  # Set the user who is deleting the record
		)
		record.delete()
		messages.success(request, "Record Deleted Successfully!")
		return redirect('home')
	else:
		messages.error(request, "You Must Be Logged In To Do That")
		return redirect('login')  # Redirect to login page if not authenticated

def add_record(request):
	if request.user.is_authenticated:
		if request.method == "POST":
			form = AddRecordForm(request.POST)
			if form.is_valid():
				new_record = form.save(commit=False)  # Don't save to DB yet
				new_record.modified_by = request.user  # Set the user who is adding the record
				new_record.save()  # Now save to DB
				messages.success(request, "Record Added!")
				return redirect('home')
		else:
			form = AddRecordForm()
		return render(request, 'add_record.html', {'form': form})
	else:
		messages.success(request, "You Must Be Logged In To Do This")
		return redirect('home')


def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		form = AddRecordForm(request.POST or None, instance=current_record)
		if request.method == "POST":
			if form.is_valid():
				updated_record = form.save(commit=False)  # Don't save to DB yet
				updated_record.modified_by = request.user  # Set the user who is updating the record
				updated_record.save()  # Now save to DB
				messages.success(request, "Record Has Been Updated!")
				return redirect('home')
		return render(request, 'update_record.html', {'form': form})
	else:
		messages.success(request, "You Must Be Logged In To Do This")
		return redirect('home')


@login_required
def audit_logs(request):
	logs = AuditLog.objects.all().order_by('-timestamp')
	return render(request, 'audit_logs.html', {'logs': logs})