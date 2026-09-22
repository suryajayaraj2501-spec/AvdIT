from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from freelancers.models import Skill, FreelancerProfile, FreelancerSkill, PortfolioItem
from clients.models import ClientProfile
from teams.models import Team, TeamMember, TeamSkill
from projects.models import Project, ProjectSkill, Milestone, Task
from services.models import Service, ServicePackage
from proposals.models import Proposal, Contract
from reviews.models import Review
from payments.models import Payment, Transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds comprehensive realistic sample data for the AdvIT Marketplace"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding AdvIT sample data..."))

        # 1. Superuser / Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@advit.ai',
                'first_name': 'AdvIT',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # 2. Skills
        skill_data = [
            ('Python', Skill.Category.DEVELOPMENT, 'bi-code-slash'),
            ('Django', Skill.Category.DEVELOPMENT, 'bi-server'),
            ('React', Skill.Category.DEVELOPMENT, 'bi-code-square'),
            ('Next.js', Skill.Category.DEVELOPMENT, 'bi-window-stack'),
            ('TypeScript', Skill.Category.DEVELOPMENT, 'bi-filetype-tsx'),
            ('Google Gemini API', Skill.Category.AI_DATA, 'bi-stars'),
            ('Machine Learning', Skill.Category.AI_DATA, 'bi-cpu'),
            ('NLP & LLMs', Skill.Category.AI_DATA, 'bi-chat-left-dots'),
            ('UI/UX Design', Skill.Category.DESIGN, 'bi-palette'),
            ('Figma', Skill.Category.DESIGN, 'bi-bezier'),
            ('PostgreSQL', Skill.Category.DEVOPS, 'bi-database'),
            ('Docker & Kubernetes', Skill.Category.DEVOPS, 'bi-boxes'),
            ('Flutter & React Native', Skill.Category.MOBILE, 'bi-phone'),
            ('QA & Test Automation', Skill.Category.OTHER, 'bi-shield-check'),
        ]

        skills_dict = {}
        for name, cat, icon in skill_data:
            s, _ = Skill.objects.get_or_create(name=name, defaults={'category': cat, 'icon': icon})
            skills_dict[name] = s

        # 3. Client Users & Profiles
        clients_info = [
            ('tech_client', 'alex@technova.io', 'Alex', 'Vance', 'TechNova AI Labs', 'AI & Cloud SaaS', '51-200', 'San Francisco, CA'),
            ('health_client', 'elena@healthbridge.com', 'Elena', 'Silva', 'HealthBridge Systems', 'Healthcare Technology', '11-50', 'Boston, MA'),
            ('fintech_client', 'marcus@finedge.co', 'Marcus', 'Sterling', 'FinEdge Global', 'Fintech & Payments', '200+', 'London, UK'),
        ]

        clients_list = []
        for uname, email, fname, lname, comp, ind, size, loc in clients_info:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'role': User.Role.CLIENT,
                    'location': loc
                }
            )
            u.set_password('pass1234')
            u.save()

            cp, _ = ClientProfile.objects.get_or_create(
                user=u,
                defaults={
                    'company_name': comp,
                    'industry': ind,
                    'company_size': size,
                    'location': loc,
                    'about_company': f"{comp} is building cutting-edge software solutions."
                }
            )
            clients_list.append(cp)

        # 4. Freelancer Users & Profiles
        freelancers_info = [
            ('sarah_chen', 'sarah@ai.dev', 'Sarah', 'Chen', 'Senior Full-Stack AI Engineer', 65.00, 'available', 'expert', 'Seattle, WA', 'Passionate full-stack developer with 7+ years of experience integrating LLM workflows, Django, and React.', ['Python', 'Django', 'Google Gemini API', 'React', 'PostgreSQL']),
            ('miguel_santos', 'miguel@design.io', 'Miguel', 'Santos', 'Principal UI/UX & Product Designer', 55.00, 'available', 'expert', 'Austin, TX', 'Award-winning product designer specialized in SaaS design systems, user journeys, and high-converting interfaces in Figma.', ['UI/UX Design', 'Figma', 'React']),
            ('devon_kim', 'devon@cloud.dev', 'Devon', 'Kim', 'Cloud Architect & DevOps Engineer', 70.00, 'busy', 'expert', 'Toronto, CA', 'Specialist in container orchestration, CI/CD pipelines, Docker, Kubernetes, and secure enterprise infrastructure.', ['Docker & Kubernetes', 'PostgreSQL', 'Python']),
            ('priya_sharma', 'priya@ml.ai', 'Priya', 'Sharma', 'NLP & AI Prompt Systems Specialist', 60.00, 'available', 'intermediate', 'Bengaluru, IN', 'Expert in fine-tuning embeddings, Google Gemini pipelines, retrieval-augmented generation, and automated workflows.', ['Google Gemini API', 'NLP & LLMs', 'Machine Learning', 'Python']),
            ('lucas_meyer', 'lucas@qa.dev', 'Lucas', 'Meyer', 'Lead QA Automation Engineer', 45.00, 'available', 'intermediate', 'Berlin, DE', 'Dedicated quality assurance engineer ensuring robust test coverage, security verification, and performance benchmarks.', ['QA & Test Automation', 'Python', 'Docker & Kubernetes']),
        ]

        freelancers_list = []
        for uname, email, fname, lname, title, rate, avail, exp, loc, bio, fskills in freelancers_info:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'role': User.Role.FREELANCER,
                    'location': loc,
                    'bio': bio
                }
            )
            u.set_password('pass1234')
            u.save()

            fp, _ = FreelancerProfile.objects.get_or_create(
                user=u,
                defaults={
                    'title': title,
                    'hourly_rate': rate,
                    'availability': avail,
                    'experience_level': exp,
                    'location': loc,
                    'bio': bio,
                    'rating': 4.95,
                    'total_reviews_count': 14,
                    'completed_projects_count': 18,
                    'total_earnings': 14500.00
                }
            )

            # Add skills
            for sk_name in fskills:
                if sk_name in skills_dict:
                    FreelancerSkill.objects.get_or_create(
                        freelancer=fp,
                        skill=skills_dict[sk_name],
                        defaults={'proficiency': FreelancerSkill.Proficiency.EXPERT, 'years_of_experience': 4}
                    )

            # Add portfolio demo item
            PortfolioItem.objects.get_or_create(
                freelancer=fp,
                title=f"{title} - Production Live Case Study",
                defaults={
                    'category': 'Web Application' if 'Full-Stack' in title else ('UI/UX Design' if 'Designer' in title else 'Cloud & DevOps'),
                    'description': f'Full-scale prototype demonstrating robust architecture, high test coverage, and clean responsive UI design by {fname}.',
                    'project_url': 'https://github.com',
                    'github_url': 'https://github.com',
                    'tags': ', '.join(fskills[:3])
                }
            )

            freelancers_list.append(fp)

        # 5. Pre-formed Team Squads
        apex_team, _ = Team.objects.get_or_create(
            name='Apex AI Studio Squad',
            defaults={
                'created_by': freelancers_list[0].user,  # Sarah Chen as Lead
                'tagline': 'High-velocity full-stack squad specialized in LLMs, Gemini AI, and resilient web platforms.',
                'description': 'Apex AI is a cohesive multidisciplinary squad consisting of an AI Lead Architect, UI/UX Designer, Cloud Engineer, and QA Specialist.',
                'hourly_rate': 180.00,
                'rating': 5.00,
                'reviews_count': 12,
                'completed_projects_count': 8,
                'is_available': True
            }
        )

        # Add squad members
        TeamMember.objects.get_or_create(team=apex_team, user=freelancers_list[0].user, defaults={'role_in_team': TeamMember.TeamRole.LEAD, 'is_lead': True})
        TeamMember.objects.get_or_create(team=apex_team, user=freelancers_list[1].user, defaults={'role_in_team': TeamMember.TeamRole.UI_UX})
        TeamMember.objects.get_or_create(team=apex_team, user=freelancers_list[2].user, defaults={'role_in_team': TeamMember.TeamRole.DEVOPS})
        TeamMember.objects.get_or_create(team=apex_team, user=freelancers_list[3].user, defaults={'role_in_team': TeamMember.TeamRole.AI_DEV})

        for s_name in ['Python', 'Django', 'Google Gemini API', 'UI/UX Design', 'Docker & Kubernetes']:
            if s_name in skills_dict:
                TeamSkill.objects.get_or_create(team=apex_team, skill=skills_dict[s_name])

        # Squad Demo Project
        PortfolioItem.objects.get_or_create(
            freelancer=freelancers_list[0],
            team=apex_team,
            title='Enterprise AI Healthcare Diagnostics & Vector Search Portal',
            defaults={
                'category': 'AI & Machine Learning',
                'description': 'Built collaboratively by Apex AI Studio squad (Architect + UI/UX + DevOps + AI Engineer). Features medical report analysis with Google Gemini API, interactive Chart.js analytics, and automated PDF export.',
                'project_url': 'https://github.com',
                'github_url': 'https://github.com',
                'tags': 'Google Gemini API, Python, Django, React, Docker'
            }
        )

        # 6. Projects & Milestones
        proj1, _ = Project.objects.get_or_create(
            title='AI-Powered Healthcare Diagnostic & Analytics SaaS',
            defaults={
                'client': clients_list[0],
                'description': 'We require a HIPAA-compliant web platform integrating Google Gemini API for medical report summarization, intuitive dashboard visualizations with Chart.js, and multi-tenant authentication.',
                'category': Project.Category.AI_ML,
                'project_type': Project.ProjectType.TEAM,
                'budget': 3500.00,
                'status': Project.Status.IN_PROGRESS
            }
        )
        for s_name in ['Python', 'Django', 'Google Gemini API', 'UI/UX Design']:
            ProjectSkill.objects.get_or_create(project=proj1, skill=skills_dict[s_name])

        # Proposal & Contract for Proj1
        prop1, _ = Proposal.objects.get_or_create(
            project=proj1,
            team=apex_team,
            defaults={
                'bid_amount': 3400.00,
                'cover_letter': 'Apex AI squad is uniquely positioned to build your healthcare analytics platform with complete end-to-end security and Gemini AI integration.',
                'estimated_duration_days': 21,
                'status': Proposal.Status.ACCEPTED
            }
        )

        contract1, _ = Contract.objects.get_or_create(
            proposal=prop1,
            defaults={
                'project': proj1,
                'client': clients_list[0],
                'team': apex_team,
                'total_amount': 3400.00,
                'status': Contract.Status.ACTIVE
            }
        )

        # Milestones for Proj1
        m1, _ = Milestone.objects.get_or_create(
            project=proj1,
            contract=contract1,
            title='Milestone 1: Database Architecture & Gemini AI Pipeline',
            defaults={
                'description': 'Setup Django models, secure auth, and connect Gemini API summarization endpoints.',
                'amount': 1400.00,
                'status': Milestone.Status.FUNDED
            }
        )
        m2, _ = Milestone.objects.get_or_create(
            project=proj1,
            contract=contract1,
            title='Milestone 2: Responsive Frontend UI & Interactive Analytics',
            defaults={
                'description': 'Implement Bootstrap 5 dashboard with Chart.js reports and task tracking.',
                'amount': 1200.00,
                'status': Milestone.Status.PENDING
            }
        )
        m3, _ = Milestone.objects.get_or_create(
            project=proj1,
            contract=contract1,
            title='Milestone 3: Security Hardening & Production Deployment',
            defaults={
                'description': 'Complete automated testing suite, Dockerize application, and deliver handover documentation.',
                'amount': 800.00,
                'status': Milestone.Status.PENDING
            }
        )

        # Tasks under Milestone 1
        Task.objects.get_or_create(milestone=m1, title='Setup Custom User & Role Models', defaults={'status': Task.Status.DONE, 'assignee': freelancers_list[0].user})
        Task.objects.get_or_create(milestone=m1, title='Design Gemini Prompt Workflow & Error Fallbacks', defaults={'status': Task.Status.IN_PROGRESS, 'assignee': freelancers_list[3].user})
        Task.objects.get_or_create(milestone=m1, title='Figma Wireframes & Design System', defaults={'status': Task.Status.DONE, 'assignee': freelancers_list[1].user})

        # Open Project 2
        proj2, _ = Project.objects.get_or_create(
            title='Real-time Multi-Vendor E-Commerce Platform',
            defaults={
                'client': clients_list[1],
                'description': 'Looking for a talented solo developer or squad to build an e-commerce platform with automated payments, product reviews, and customer messaging.',
                'category': Project.Category.WEB,
                'project_type': Project.ProjectType.EITHER,
                'budget': 1800.00,
                'status': Project.Status.OPEN
            }
        )
        for s_name in ['Python', 'Django', 'PostgreSQL', 'UI/UX Design']:
            ProjectSkill.objects.get_or_create(project=proj2, skill=skills_dict[s_name])

        # 7. Services Marketplace Packages
        srv1, _ = Service.objects.get_or_create(
            freelancer=freelancers_list[0],
            title='I will build a custom full-stack AI web application with Django and Gemini',
            defaults={
                'category': Service.Category.AI_SERVICES,
                'description': 'Get a production-grade web application with custom AI features, modern UI, secure authentication, and scalable database architecture.',
                'rating': 5.00,
                'orders_count': 14,
                'is_active': True
            }
        )
        ServicePackage.objects.get_or_create(
            service=srv1,
            tier=ServicePackage.Tier.BASIC,
            defaults={
                'name': 'AI Starter MVP',
                'description': 'Single-page web app with Gemini AI prompt integration and clean UI.',
                'price': 150.00,
                'delivery_days': 4,
                'revisions': 2,
                'features': ['Gemini API Integration', 'Responsive UI', 'Source Code Included']
            }
        )
        ServicePackage.objects.get_or_create(
            service=srv1,
            tier=ServicePackage.Tier.STANDARD,
            defaults={
                'name': 'Full-Stack AI Application',
                'description': 'Multi-page application with database storage, user auth, and dashboard.',
                'price': 450.00,
                'delivery_days': 8,
                'revisions': 4,
                'features': ['Full Django + REST API', 'Gemini AI Pipelines', 'Database & Auth', 'Chart.js Analytics']
            }
        )
        ServicePackage.objects.get_or_create(
            service=srv1,
            tier=ServicePackage.Tier.PREMIUM,
            defaults={
                'name': 'Enterprise AI SaaS Suite',
                'description': 'Complete SaaS platform with payment gateway, squad roles, and Docker deployment.',
                'price': 950.00,
                'delivery_days': 15,
                'revisions': 6,
                'features': ['Full Enterprise Architecture', 'Escrow / Razorpay Integration', 'Docker & CI/CD', 'Priority Support']
            }
        )

        # 8. Payments & Escrow Ledger Records
        pay1, _ = Payment.objects.get_or_create(
            milestone=m1,
            contract=contract1,
            payer=clients_list[0].user,
            payee=freelancers_list[0].user,
            amount=1400.00,
            defaults={
                'status': Payment.Status.ESCROW_FUNDED,
                'razorpay_order_id': 'order_seed_998811',
                'razorpay_payment_id': 'pay_seed_223344'
            }
        )
        Transaction.objects.get_or_create(
            user=clients_list[0].user,
            payment=pay1,
            transaction_type=Transaction.TxType.ESCROW_DEPOSIT,
            defaults={
                'amount': 1400.00,
                'status': Transaction.Status.SUCCESS,
                'description': f"Funded escrow for {m1.title}"
            }
        )

        # 9. Reviews
        Review.objects.get_or_create(
            reviewer=clients_list[0].user,
            reviewee=freelancers_list[0].user,
            defaults={
                'rating': 5,
                'target_type': Review.TargetType.FREELANCER,
                'comment': 'Sarah and the Apex squad delivered outstanding work ahead of schedule! The Gemini AI integration is seamless.'
            }
        )

        self.stdout.write(self.style.SUCCESS("AdvIT sample database successfully seeded!"))
        self.stdout.write(self.style.SUCCESS("Default credentials: admin / admin123 (Staff), tech_client / pass1234 (Client), sarah_chen / pass1234 (Freelancer)"))
