import unittest
import genesis

class TestGenesis(unittest.TestCase):

    def test_login(self):
        project = genesis.Project(debug=True)
        self.assertEqual(project.login('http://rukia/api', 'aadesada', 'eaxum'), 'Aderemi Adesada')
        self.assertEqual(project.login('http://rukia/api', 'aadesad', 'eaxum') ,
                                       'Login failure, Wrong credentials. pls check login details or host')
        self.assertEqual(project.login('http://rukia/api', 'aadesada', 'eaxu'),
                         'Login failure, Wrong credentials. pls check login details or host')
        self.assertEqual(project.login('http://rukia/ap', 'aadesada', 'eaxum'),
                         'invalid host url')
        self.assertEqual(project.login('http//rukia/api', 'aadesada', 'eaxum'),
                         'bad schema or bad connection')
        self.assertEqual(project.login('http:/rukia/api', 'aadesada', 'eaxum'),
                         'invalid host url')

    def test_file_gen(self):
        pass




if __name__ == '__main__':
    unittest.main()