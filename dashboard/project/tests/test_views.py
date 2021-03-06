from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import simplejson

from dashboard.project.views import run_task
from dashboard.project.models import Analysis


class TestViews(TestCase):
    fixtures = ['project.json', 'analysis.json']

    def setUp(self):
        self.analysis = Analysis.objects.get(id=1)

    def test_project_details_should_be_acessible(self):
        url = '/project/%d/' % self.analysis.project.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_absent_project_should_not_be_acessible(self):
        url = '/project/999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_project_analyze_should_be_acessible(self):
        url = '/project/%d/analyze/' % self.analysis.project.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_absent_project_analyze_should_not_be_acessible(self):
        url = '/project/999/analyze/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_should_show_projects_and_get_200(self):
        url = "/projects/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_should_visit_create_project_and_get_200(self):
        url = "/project/create"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_history_should_be_acessible(self):
        url = '/project/%d/history/pep8.json' % self.analysis.project.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_history_with_invalid_metric_name_should_not_be_acessible(self):
        url = '/project/%d/history/pep999.json' % self.analysis.project.id
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_project_history_returns_correct_json(self):
        url = '/project/%d/history/pep8.json' % self.analysis.project.id
        response = self.client.get(url)
        content_type = response.items().pop()[1]
        content = simplejson.loads(response.content)
        self.assertEqual(content_type, 'application/json')
        self.assertEqual(len(content['dates']), 2)
        self.assertEqual(len(content['metric_analysis']), 2)


class TestRunTaskView(TestCase):
    fixtures = ['project.json', 'analysis.json']

    def setUp(self):
        self.tasks = ['pep8', 'pyflakes', 'clonedigger', 'jshint', 'csslint']

    def test_access_default_tasks(self):
        for task in self.tasks:
            response = self.client.get('/project/1/%s/' % task)
            self.assertEqual(200, response.status_code)

    def test_task_should_be_return_number_of_errors(self):
        errors_per_task = {
            'pep8': '3',
            'pyflakes': '2',
            'clonedigger': '20',
            'jshint': '2',
            'csslint': '6',
        }

        request = RequestFactory().get('/project/1/task')

        for task in self.tasks:
            response = run_task(request, project_id=1, task=task)
            self.assertEqual(errors_per_task[task], response.content)

    def test_should_be_return_404_for_inexistent_task(self):
        response = self.client.get('/project/1/inexistent_task/')
        self.assertEqual(404, response.status_code)
