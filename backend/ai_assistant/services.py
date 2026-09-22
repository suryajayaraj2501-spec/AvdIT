import os
import json
import re
from django.conf import settings
from freelancers.models import Skill, FreelancerProfile
from teams.models import Team

try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiService:
    @classmethod
    def get_api_key(cls):
        return getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

    @classmethod
    def get_client(cls):
        api_key = cls.get_api_key()
        if not api_key or not GENAI_AVAILABLE:
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception:
            return None

    @classmethod
    def get_model(cls):
        """Returns a callable that generates content, or None if unavailable."""
        client = cls.get_client()
        if not client:
            return None
        return client


    @classmethod
    def clean_json_response(cls, text):
        """Extract and parse JSON safely from LLM output."""
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try regex search for markdown fenced JSON code block
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except Exception:
                pass

        # Try finding outermost braces or brackets
        b_start = text.find('{')
        b_end = text.rfind('}')
        if b_start != -1 and b_end != -1 and b_end > b_start:
            try:
                return json.loads(text[b_start:b_end+1])
            except Exception:
                pass

        arr_start = text.find('[')
        arr_end = text.rfind(']')
        if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
            try:
                return json.loads(text[arr_start:arr_end+1])
            except Exception:
                pass

        return None

    # =========================================================================
    # 1. AI Team Builder ⭐
    # =========================================================================
    @classmethod
    def build_team_recommendation(cls, project_title, description, budget=1000, category='Full-Stack Product'):
        prompt = f"""
You are an expert Chief Technology Officer and Agile Squad Architect for AdvIT.
Analyze the following project and construct an optimal, multidisciplinary team structure.

Project Title: {project_title}
Category: {category}
Budget: ${budget}
Description:
{description}

Respond ONLY with a valid JSON object formatted exactly as:
{{
  "project_summary": "Brief 1-2 sentence executive scope",
  "recommended_squad_size": 4,
  "estimated_weeks": 3,
  "required_skills": ["Python", "Django", "React", "UI/UX", "PostgreSQL", "Gemini API"],
  "roles": [
    {{
      "role": "Team Lead & Full-Stack Architect",
      "primary_skills": ["Django", "Python", "System Architecture"],
      "responsibilities": "Oversee system architecture, database design, API design and code quality.",
      "estimated_allocation": "100%",
      "recommended_experience": "Expert"
    }},
    {{
      "role": "Frontend / UI/UX Specialist",
      "primary_skills": ["React", "CSS", "Responsive UI"],
      "responsibilities": "Build sleek responsive interfaces and user experience.",
      "estimated_allocation": "80%",
      "recommended_experience": "Intermediate"
    }},
    {{
      "role": "AI / ML Integration Engineer",
      "primary_skills": ["Gemini API", "Prompt Engineering", "NLP"],
      "responsibilities": "Integrate AI workflows and fine-tune prompt endpoints.",
      "estimated_allocation": "60%",
      "recommended_experience": "Intermediate"
    }},
    {{
      "role": "QA & Test Automation Specialist",
      "primary_skills": ["Test Automation", "Security", "CI/CD"],
      "responsibilities": "Test coverage, integration testing, and release validation.",
      "estimated_allocation": "40%",
      "recommended_experience": "Intermediate"
    }}
  ]
}}
"""
        model = cls.get_model()
        structured_res = None

        if model:
            try:
                response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                structured_res = cls.clean_json_response(response.text)
            except Exception:
                structured_res = None

        # Fallback intelligent rule-based engine if offline or API key missing
        if not structured_res:
            structured_res = cls._fallback_team_builder(project_title, description, budget, category)

        # Query Database for Matching Talent & Teams
        extracted_skills = structured_res.get('required_skills', ['Python', 'Web Development', 'Design'])
        matching_freelancers = cls._match_freelancers_from_db(extracted_skills)
        matching_teams = cls._match_teams_from_db(extracted_skills)

        return {
            'analysis': structured_res,
            'matching_freelancers': matching_freelancers,
            'matching_teams': matching_teams,
            'is_ai_powered': bool(model is not None)
        }

    @classmethod
    def _fallback_team_builder(cls, title, desc, budget, category):
        """High-quality heuristic squad composer when Gemini API is unavailable."""
        desc_lower = desc.lower()
        skills = []
        roles = []

        if 'ai' in desc_lower or 'llm' in desc_lower or 'gpt' in desc_lower or 'gemini' in desc_lower:
            skills.extend(['Python', 'Google Gemini API', 'Django', 'Prompt Engineering'])
            roles.append({
                'role': 'AI / ML Engineer',
                'primary_skills': ['Gemini API', 'Python', 'Embeddings'],
                'responsibilities': 'Develop LLM pipelines, prompt workflows, and AI services.',
                'estimated_allocation': '100%',
                'recommended_experience': 'Expert'
            })

        if 'design' in desc_lower or 'ui' in desc_lower or 'ux' in desc_lower or 'mobile' in desc_lower:
            skills.extend(['UI/UX Design', 'Figma', 'Responsive CSS'])
            roles.append({
                'role': 'UI/UX & Product Designer',
                'primary_skills': ['UI/UX Design', 'Wireframing', 'Figma'],
                'responsibilities': 'Craft user journeys, interface prototypes, and design systems.',
                'estimated_allocation': '75%',
                'recommended_experience': 'Intermediate'
            })

        # Core developer roles
        skills.extend(['Django', 'Python', 'JavaScript', 'HTML/CSS', 'PostgreSQL'])
        roles.append({
            'role': 'Full-Stack Lead Developer',
            'primary_skills': ['Django', 'Python', 'REST APIs'],
            'responsibilities': 'Architect backend services, database schema, and authentication.',
            'estimated_allocation': '100%',
            'recommended_experience': 'Expert'
        })
        roles.append({
            'role': 'QA & Test Specialist',
            'primary_skills': ['Automated Testing', 'Bug Tracking'],
            'responsibilities': 'Verify end-to-end user workflows and cross-device testing.',
            'estimated_allocation': '50%',
            'recommended_experience': 'Intermediate'
        })

        return {
            'project_summary': f"Custom {category} execution with tailored AI squad.",
            'recommended_squad_size': len(roles),
            'estimated_weeks': 3 if float(budget) < 2000 else 6,
            'required_skills': list(set(skills)),
            'roles': roles
        }

    @classmethod
    def _match_freelancers_from_db(cls, required_skills):
        freelancers = FreelancerProfile.objects.select_related('user').prefetch_related('freelancer_skills__skill').filter(availability__in=['available', 'busy'])
        results = []

        for fl in freelancers:
            fl_skills = [fs.skill.name.lower() for fs in fl.freelancer_skills.all()]
            overlap = 0
            for req in required_skills:
                if any(req.lower() in fs or fs in req.lower() for fs in fl_skills):
                    overlap += 1

            # Match score formula: skill overlap + rating boost
            match_score = int(min(98, (overlap / max(1, len(required_skills)) * 70) + (float(fl.rating) * 5) + 5))
            if overlap > 0 or len(results) < 4:
                results.append({
                    'id': fl.id,
                    'user_id': fl.user.id,
                    'name': fl.user.display_name,
                    'title': fl.title,
                    'hourly_rate': float(fl.hourly_rate),
                    'rating': float(fl.rating),
                    'reviews_count': fl.total_reviews_count,
                    'avatar': fl.user.avatar.url if fl.user.avatar else None,
                    'match_score': match_score,
                    'skills': [fs.skill.name for fs in fl.freelancer_skills.all()[:4]]
                })

        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:6]

    @classmethod
    def _match_teams_from_db(cls, required_skills):
        teams = Team.objects.filter(is_available=True).prefetch_related('members__user', 'team_skills__skill')
        results = []

        for t in teams:
            t_skills = [ts.skill.name.lower() for ts in t.team_skills.all()]
            overlap = 0
            for req in required_skills:
                if any(req.lower() in ts or ts in req.lower() for ts in t_skills):
                    overlap += 1

            match_score = int(min(99, (overlap / max(1, len(required_skills)) * 75) + (float(t.rating) * 4) + 8))
            results.append({
                'id': t.id,
                'name': t.name,
                'slug': t.slug,
                'tagline': t.tagline,
                'hourly_rate': float(t.hourly_rate),
                'rating': float(t.rating),
                'member_count': t.members.count(),
                'match_score': match_score,
                'avatar': t.avatar.url if t.avatar else None,
                'skills': [ts.skill.name for ts in t.team_skills.all()[:4]]
            })

        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:4]

    # =========================================================================
    # 2. AI Proposal Generator
    # =========================================================================
    @classmethod
    def generate_proposal_draft(cls, project_title, project_desc, freelancer_name, freelancer_bio, skills_list):
        prompt = f"""
You are an elite freelance consultant. Write a highly compelling, professional proposal cover letter.

Project Title: {project_title}
Project Requirements:
{project_desc}

Freelancer Name: {freelancer_name}
Freelancer Bio: {freelancer_bio}
Freelancer Skills: {', '.join(skills_list)}

Include:
1. Enthusiastic greeting and understanding of the project objectives.
2. Technical approach explaining how you will implement the solution.
3. Relevant experience and why you are the ideal fit.
4. Proposed milestone milestones breakdown.
5. Professional call to action.

Return plain text suitable to paste directly as a cover letter.
"""
        model = cls.get_model()
        if model:
            try:
                response = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                return response.text.strip()
            except Exception:
                pass

        # Fallback template
        return f"""Dear Client,

I am excited to apply for your project "{project_title}". Having thoroughly reviewed your project requirements, I am confident that my experience in {', '.join(skills_list[:3])} makes me an ideal fit.

### Technical Approach & Deliverables
1. **Architecture & Scope Alignment:** Review key requirements and establish core data models.
2. **Implementation:** Develop clean, scalable code adhering to industry best practices.
3. **Quality Assurance & Verification:** Comprehensive automated testing and UI validation.

I have completed similar projects with high client ratings and look forward to discussing the milestones with you.

Best regards,
{freelancer_name}"""

    # =========================================================================
    # 3. AI Profile Improver
    # =========================================================================
    @classmethod
    def audit_and_improve_profile(cls, title, bio, current_skills, hourly_rate):
        prompt = f"""
You are a career coach and profile optimizer for AdvIT freelancers.
Analyze this profile:
Title: {title}
Hourly Rate: ${hourly_rate}
Skills: {', '.join(current_skills)}
Bio:
{bio}

Provide actionable suggestions formatted as JSON:
{{
  "improved_title": "Optimized high-converting title",
  "bio_feedback": "Critique of current bio",
  "improved_bio": "Rewritten persuasive bio highlighting value proposition",
  "recommended_skills_to_add": ["Skill 1", "Skill 2", "Skill 3"],
  "pricing_tip": "Advice on pricing strategy"
}}
"""
        model = cls.get_model()
        if model:
            try:
                res = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                parsed = cls.clean_json_response(res.text)
                if parsed:
                    return parsed
            except Exception:
                pass

        return {
            "improved_title": f"Senior {title} | AI & Full-Stack Specialist",
            "bio_feedback": "Add more quantified achievements and highlight your team collaboration experience.",
            "improved_bio": f"I am a results-oriented {title} with expertise in building scalable, production-grade applications. Passionate about delivering clean code, intuitive user experiences, and AI-driven solutions.",
            "recommended_skills_to_add": ["Google Gemini API", "System Design", "CI/CD & Docker", "Automated Testing"],
            "pricing_tip": f"Your current rate of ${hourly_rate}/hr is competitive. As you complete team squad projects, consider adjusting to ${float(hourly_rate) + 15}/hr."
        }

    # =========================================================================
    # 4. AI Project Assistant (Decompose into Milestones & Tasks)
    # =========================================================================
    @classmethod
    def decompose_project(cls, project_title, project_desc, budget):
        prompt = f"""
Decompose this project into 3 to 4 sequential milestones with estimated costs and specific sub-tasks.
Project: {project_title}
Budget: ${budget}
Description: {project_desc}

Respond ONLY with valid JSON:
{{
  "milestones": [
    {{
      "title": "Milestone 1: Architecture & Foundation",
      "amount": 300,
      "due_days": 5,
      "tasks": ["Setup Repository & CI", "Design Database Schema", "Implement Authentication & Roles"]
    }},
    {{
      "title": "Milestone 2: Core Feature Implementation",
      "amount": 450,
      "due_days": 12,
      "tasks": ["Build Core APIs", "Develop Frontend UI & Components", "Integrate Third-party Services"]
    }},
    {{
      "title": "Milestone 3: AI Integration & Testing",
      "amount": 250,
      "due_days": 18,
      "tasks": ["Integrate Gemini AI endpoints", "End-to-end testing", "Production Deployment"]
    }}
  ]
}}
"""
        model = cls.get_model()
        if model:
            try:
                res = model.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                parsed = cls.clean_json_response(res.text)
                if parsed:
                    return parsed
            except Exception:
                pass

        total = float(budget)
        return {
            "milestones": [
                {
                    "title": "Milestone 1: Project Architecture & Setup",
                    "amount": round(total * 0.35, 2),
                    "due_days": 5,
                    "tasks": ["Setup environment & database models", "Design initial UI wireframes", "Configure role permissions"]
                },
                {
                    "title": "Milestone 2: Core Features & AI Workflows",
                    "amount": round(total * 0.45, 2),
                    "due_days": 12,
                    "tasks": ["Implement main application logic", "Build responsive user views", "Connect AI matching and services"]
                },
                {
                    "title": "Milestone 3: Testing, Security & Handover",
                    "amount": round(total * 0.20, 2),
                    "due_days": 18,
                    "tasks": ["End-to-end integration tests", "Performance optimization", "Final documentation & deployment"]
                }
            ]
        }

    # =========================================================================
    # 5. AI Chatbot Assistant
    # =========================================================================
    @classmethod
    def get_chatbot_response(cls, user_message, conversation_history=None):
        system_prompt = """
You are AdvIT Co-Pilot, the friendly, highly intelligent AI assistant for AdvIT (an AI-Powered Team-Based Freelancing Marketplace).
AdvIT connects clients with top solo freelancers and multidisciplinary squads (e.g. Designer + Frontend + Backend + AI Engineer + QA).
Platform capabilities:
- AI Team Builder: Clients describe projects, AdvIT scopes required roles and matches the best squad.
- Multi-tier Services: Freelancers offer Basic, Standard, and Premium packages.
- Escrow Protection: Milestone payments are held safely and released when deliverables are approved.
- Real-time Collaboration: Integrated chat, project workspaces, task boards, and file sharing.

Always provide helpful, polite, and concise answers. If a user describes a project, recommend trying the AI Team Builder or offer team role suggestions.
"""
        model = cls.get_model()
        if model:
            try:
                messages_context = f"System: {system_prompt}\n"
                if conversation_history:
                    for m in conversation_history[-4:]:
                        role_label = 'User' if m.role == 'user' else 'AdvIT AI'
                        messages_context += f"{role_label}: {m.content}\n"
                messages_context += f"User: {user_message}\nAdvIT AI:"

                res = model.models.generate_content(model='gemini-2.5-flash', contents=messages_context)
                reply = res.text.strip()
                return {'reply': reply, 'structured_data': {}}
            except Exception:
                pass

        # Intelligent Fallback Responses
        msg_lower = user_message.lower()
        if 'team' in msg_lower or 'squad' in msg_lower or 'hire' in msg_lower:
            return {
                'reply': "AdvIT specializes in forming multidisciplinary squads! You can use our **AI Team Builder** to automatically scope required roles and assemble an optimal team of designers, full-stack engineers, and AI specialists.",
                'structured_data': {
                    'team_recommendations': [
                        {'role': 'UI/UX Designer', 'description': 'Crafts interface systems & Figma prototypes'},
                        {'role': 'Full-Stack Developer', 'description': 'Builds Django REST APIs & responsive frontends'},
                        {'role': 'AI / ML Engineer', 'description': 'Integrates Gemini LLM workflows'}
                    ]
                }
            }
        elif 'payment' in msg_lower or 'escrow' in msg_lower or 'razorpay' in msg_lower:
            return {
                'reply': "All project milestones on AdvIT are protected by our **Escrow Vault**. When a client funds a milestone, payments are safely locked and only transferred to the freelancer or team upon your final approval.",
                'structured_data': {}
            }
        elif 'service' in msg_lower or 'fiverr' in msg_lower or 'package' in msg_lower:
            return {
                'reply': "Freelancers on AdvIT can offer 3-tier packaged services (Basic, Standard, and Premium) with transparent pricing, delivery timelines, and revision guarantees.",
                'structured_data': {}
            }
        else:
            return {
                'reply': f"I'm here to help you navigate AdvIT! You can explore projects, discover AI-recommended squads, or offer packaged services. What would you like to build or accomplish today?",
                'structured_data': {}
            }
