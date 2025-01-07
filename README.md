# Інструкція для WarSprit

## Налаштування середовища

1. **Створіть віртуальне середовище:**
   ```bash
   python -m venv venv
   ```
2. **Активуйте віртуальне середовище:**

    Для Windows:
   ```bash
   venv\Scripts\activate
   ```
   Для macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
3. Встановіть залежності з файлу requirements.txt:

   ```bash
   python manage.py makemigrations
   ```
   
   ```bash
   python manage.py migrate
   ```
   
   ```bash
   pip install -r requirements.txt
   ```
      
   ```bash
   python manage.py runserver
   ```
   


  ```bash
   python manage.py collectstatic
   ```