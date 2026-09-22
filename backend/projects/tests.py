from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clients.models import ClientProfile
from freelancers.models import Skill
from projects.models import Project, Milestone, Task

User = get_user_model()


class ProjectsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='proj_client', password='Pass1234!', role=User.Role.CLIENT)
        self.client_profile = ClientProfile.objects.create(user=self.user, company_name='Test Corp')
        self.skill = Skill.objects.create(name='Django', category=Skill.Category.DEVELOPMENT)

    def test_project_creation_and_workspace(self):
        self.client.login(username='proj_client', password='Pass1234!')
        create_url = reverse('projects:create')
        data = {
            'title': 'AI Web App',
            'description': 'Build an advanced web application with AI integration.',
            'category': Project.Category.AI_ML,
            'project_type': Project.ProjectType.EITHER,
            'budget': 2000,
            'skills': [self.skill.id]
        }
        res = self.client.post(create_url, data)
        self.assertEqual(res.status_code, 302)

        project = Project.objects.filter(title='AI Web App').first()
        self.assertIsNotNone(project)
        self.assertEqual(project.client, self.client_profile)
        self.assertTrue(project.skills.filter(id=self.skill.id).exists())

        # Test adding milestone
        m_url = reverse('projects:add_milestone', kwargs={'project_id': project.id})
        m_res = self.client.post(m_url, {'title': 'Milestone 1', 'amount': 1000, 'description': 'Deliverable 1'})
        self.assertEqual(m_res.status_code, 302)
        self.assertEqual(project.milestones.count(), 1)
