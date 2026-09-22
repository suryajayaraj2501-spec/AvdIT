from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clients.models import ClientProfile
from freelancers.models import FreelancerProfile
from projects.models import Project, Milestone
from proposals.models import Proposal, Contract

User = get_user_model()


class ProposalsContractTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.c_user = User.objects.create_user(username='client_u', password='Pass1234!', role=User.Role.CLIENT)
        self.client_profile = ClientProfile.objects.create(user=self.c_user, company_name='Nova Corp')

        self.fl_user = User.objects.create_user(username='freelancer_u', password='Pass1234!', role=User.Role.FREELANCER)
        self.freelancer_profile = FreelancerProfile.objects.create(user=self.fl_user, title='Senior Dev')

        self.project = Project.objects.create(
            client=self.client_profile,
            title='AI Chat App',
            description='Build AI chat application',
            budget=1500,
            status=Project.Status.OPEN
        )

    def test_proposal_submission_and_acceptance_flow(self):
        # 1. Freelancer submits proposal
        self.client.login(username='freelancer_u', password='Pass1234!')
        submit_url = reverse('proposals:submit', kwargs={'project_id': self.project.id})
        res = self.client.post(submit_url, {
            'apply_as': 'solo',
            'bid_amount': 1400,
            'estimated_duration_days': 10,
            'cover_letter': 'I am the perfect match for this AI build.'
        })
        self.assertEqual(res.status_code, 302)

        proposal = Proposal.objects.filter(project=self.project, freelancer=self.freelancer_profile).first()
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.bid_amount, 1400)

        # 2. Client accepts proposal
        self.client.login(username='client_u', password='Pass1234!')
        accept_url = reverse('proposals:accept', kwargs={'proposal_id': proposal.id})
        accept_res = self.client.post(accept_url)
        self.assertEqual(accept_res.status_code, 302)

        # Verify proposal accepted & contract auto-created
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, Proposal.Status.ACCEPTED)

        contract = Contract.objects.filter(proposal=proposal).first()
        self.assertIsNotNone(contract)
        self.assertEqual(contract.total_amount, 1400)
        self.assertEqual(contract.status, Contract.Status.ACTIVE)

        # Verify project status changed to IN_PROGRESS
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.IN_PROGRESS)

        # Verify initial milestone created
        self.assertTrue(self.project.milestones.exists())
