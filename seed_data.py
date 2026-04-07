import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zenith.settings')
django.setup()

from portfolio.models import Project, Service, FAQ

def seed():
    # FAQs
    faqs_data = [
        {"question": "მუშაობთ თუ არა არსებული პროექტების მხარდაჭერაზე?", "answer": "დიახ, შემიძლია როგორც ნულიდან დაწყება, ისე არსებული კოდის აუდიტი, ბაგების გასწორება და ახალი ფუნქციების დამატება მაღალი ხარისხით.", "order": 1},
        {"question": "რა პროცესს გადის პროექტი დასაწყისიდან დასრულებამდე?", "answer": "ჩვენი პროცესი მოიცავს: 1) მოთხოვნების ანალიზი და დაგეგმვა 2) არქიტექტურის და დიზაინის შემუშავება 3) დეველოპმენტი (Backend & Frontend) 4) ტესტირება და 5) სერვერზე გაშვება (Deployment).", "order": 2},
        {"question": "უზრუნველყოფთ თუ არა საიტის მხარდაჭერას დასრულების შემდეგ?", "answer": "რა თქმა უნდა! პროექტის ჩაბარების შემდეგ, გთავაზობთ მხარდაჭერის და მართვის პაკეტებს, რათა თქვენი სისტემა მუდმივად იყოს უსაფრთხო და განახლებული.", "order": 3},
    ]
    for f in faqs_data:
        FAQ.objects.get_or_create(question=f["question"], defaults={"answer": f["answer"], "order": f["order"]})

    # Update Projects with Slugs & Case Study info
    projects_data = [
        {
            "title": "django-core-api",
            "description": "A powerful Django Backend API with secure authentication and scalable architecture.",
            "problem": "The client needed a secure, fast, and highly extensible backend system to handle a large volume of concurrent data.",
            "solution": "Developed a robust architecture using Django REST Framework, implemented JWT authentication, and utilized Docker containerization for streamlined deployment.",
            "result": "Application response time increased by 40% and the deployment cycle for new features was significantly reduced."
        },
        {
            "title": "tezeurusi-web-app",
            "description": "CRM system with real-time data synchronization.",
            "problem": "The customer relationship management process was chaotic, scattered across multiple unsynced spreadsheets.",
            "solution": "Built a React frontend integrated with Supabase, ensuring instantaneous data synchronization across all devices and users.",
            "result": "Business processes were fully automated, allowing the sales team to dedicate 30% more time to actual client interactions."
        }
    ]

    for p in projects_data:
        proj = Project.objects.filter(title=p["title"]).first()
        if proj:
            proj.slug = slugify(p["title"])
            proj.problem = p["problem"]
            proj.solution = p["solution"]
            proj.result = p["result"]
            proj.save()
        else:
            Project.objects.create(
                title=p["title"], 
                slug=slugify(p["title"]),
                description=p["description"],
                problem=p["problem"],
                solution=p["solution"],
                result=p["result"],
                technologies="Python, Django, React", 
                order=1
            )
            
    # Fix missing slugs for existing projects
    for proj in list(Project.objects.all()):
        if not proj.slug:
            proj.slug = slugify(proj.title)
            proj.save()

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
