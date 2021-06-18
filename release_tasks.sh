
echo "Running migrations..."
python manage.py migrate

echo "Creating static file dirs..."
mkdir coreapp/coreapp/static
mkdir coreapp/coreapp/staticfiles

echo "Collecting static files..."
python manage.py collectstatic