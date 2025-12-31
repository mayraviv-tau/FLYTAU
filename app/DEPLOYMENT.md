# הוראות פריסה ל-PythonAnywhere

מדריך זה מסביר כיצד לפרוס את אפליקציית FLYTAU ל-PythonAnywhere.

## דרישות מוקדמות

1. חשבון ב-PythonAnywhere (חינמי בכתובת: https://www.pythonanywhere.com)
2. גישה למסד הנתונים MySQL ב-PythonAnywhere
3. GitHub repository עם הקוד

## שלב 1: העלאת קבצים ל-PythonAnywhere

### אופציה א': העלאה מ-GitHub (מומלץ)

1. היכנסו ל-Dashboard של PythonAnywhere
2. פתחו את ה-Bash Console
3. בצעו git clone:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git flytau
   cd flytau/app
   ```

### אופציה ב': העלאה ידנית

1. היכנסו ל-Dashboard של PythonAnywhere
2. פתחו את ה-Files tab
3. צרו תיקיה חדשה: `/home/YOUR_USERNAME/flytau`
4. העלו את כל הקבצים מתיקיית `app/` לתיקיה זו

## שלב 2: התקנת Dependencies

1. פתחו Bash Console
2. התקינו את החבילות הנדרשות:
   ```bash
   cd ~/flytau/app
   pip3.10 install --user -r requirements.txt
   ```
   (החליפו `3.10` בגרסת Python שלכם, בדרך כלל 3.8, 3.9, או 3.10)

## שלב 3: יצירת קובץ Config

1. פתחו את ה-Files tab
2. נווטו ל-`/home/YOUR_USERNAME/flytau/app/`
3. צרו קובץ חדש בשם `config.py`
4. העתיקו את התוכן מ-`config.py.example` והוסיפו את הפרטים שלכם:
   ```python
   import os

   class Config:
       SECRET_KEY = 'YOUR_SECRET_KEY_HERE'  # החלפו במפתח אקראי
       DB_HOST = 'YOUR_USERNAME.mysql.pythonanywhere-services.com'
       DB_USER = 'YOUR_USERNAME'
       DB_PASSWORD = 'YOUR_DB_PASSWORD'
       DB_NAME = 'YOUR_USERNAME$flytau'
       DB_PORT = 3306
       SESSION_TYPE = 'null'  # חשוב ל-PythonAnywhere
       SESSION_PERMANENT = False
       DEBUG = False
   ```

## שלב 4: הגדרת MySQL Database

1. היכנסו ל-Databases tab ב-PythonAnywhere
2. לחצו על "Initialize MySQL database" אם זו הפעם הראשונה
3. צרו database חדש בשם `flytau` (השם המלא יהיה `YOUR_USERNAME$flytau`)
4. פתחו MySQL console:
   ```bash
   mysql -u YOUR_USERNAME -p'YOUR_PASSWORD' YOUR_USERNAME$flytau
   ```
5. הרצו את קבצי ה-SQL:
   ```sql
   source /home/YOUR_USERNAME/flytau/db/schema.sql;
   source /home/YOUR_USERNAME/flytau/db/seed.sql;
   ```
   או העתיקו את התוכן ישירות ל-MySQL console.

## שלב 5: הגדרת Web App

1. היכנסו ל-Web tab ב-PythonAnywhere
2. לחצו על "Add a new web app"
3. בחרו Flask
4. בחרו Python 3.10 (או גרסה אחרת שהתקנתם)
5. בחרו את path לפרויקט: `/home/YOUR_USERNAME/flytau/app/`
6. בחרו את WSGI file: `/home/YOUR_USERNAME/flytau/app/wsgi.py`
7. לחצו Next

## שלב 6: עדכון WSGI Configuration

1. ב-Web tab, לחצו על הקישור "WSGI configuration file"
2. עדכנו את הקובץ כך:
   ```python
   # The WSGI configuration file should already be set up correctly
   # Just make sure it points to your wsgi.py file
   ```
3. שמרו את הקובץ

## שלב 7: הגדרת Static Files

1. ב-Web tab, גללו למטה ל-"Static files"
2. הוסיפו mapping:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/flytau/app/static/`

## שלב 8: הגדרת Environment Variables (אופציונלי)

אם אתם משתמשים ב-environment variables במקום config.py:

1. ב-Web tab, גללו למטה ל-"Environment variables"
2. הוסיפו את המשתנים הבאים:
   - `DB_HOST`: `YOUR_USERNAME.mysql.pythonanywhere-services.com`
   - `DB_USER`: `YOUR_USERNAME`
   - `DB_PASSWORD`: `YOUR_DB_PASSWORD`
   - `DB_NAME`: `YOUR_USERNAME$flytau`
   - `DB_PORT`: `3306`
   - `SECRET_KEY`: `YOUR_SECRET_KEY`
   - `SESSION_TYPE`: `null`
   - `DEBUG`: `False`

## שלב 9: הרצת האפליקציה

1. ב-Web tab, לחצו על הכפתור "Reload" או "Reload YOUR_USERNAME.pythonanywhere.com"
2. פתחו את האתר שלכם: `https://YOUR_USERNAME.pythonanywhere.com`
3. האפליקציה אמורה להיות פעילה!

## פתרון בעיות נפוצות

### שגיאת Import
- ודאו שכל הקבצים נמצאים בתיקיה הנכונה
- ודאו שהמיקום ב-WSGI configuration נכון
- בדקו את ה-console logs ב-Web tab

### שגיאת Database Connection
- ודאו שפרטי ה-DB ב-config.py נכונים
- ודאו שה-database נוצר ונקרא `YOUR_USERNAME$flytau`
- בדקו שה-schema וה-seed הורצו בהצלחה

### שגיאת 404
- ודאו שה-static files מוגדרים נכון
- בדקו שה-routes נכונים ב-app.py

### שגיאת Session
- ודאו ש-SESSION_TYPE מוגדר ל-`'null'` או `'sqlalchemy'` (לא `'filesystem'`)

## עדכון הקוד

לאחר שינויים בקוד:

1. אם השתמשתם ב-git clone:
   ```bash
   cd ~/flytau
   git pull
   ```

2. אם העליתם ידנית, העלו את הקבצים החדשים

3. ב-Web tab, לחצו על "Reload"

## הערות חשובות

- PythonAnywhere תומך רק ב-Python 3.8, 3.9, או 3.10
- ה-database name תמיד יתחיל עם `YOUR_USERNAME$`
- בחשבון חינמי יש מגבלות על bandwidth ו-requests
- session files לא עובדים טוב ב-PythonAnywhere, השתמשו ב-`SESSION_TYPE = 'null'`

