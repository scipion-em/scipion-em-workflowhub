# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Irene Sanchez Lopez (isanchez@cnb.csic.es)
# *
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import requests
import yaml
import json
import subprocess
from distutils.spawn import find_executable
from pwem.protocols import EMProtocol
from pyworkflow.protocol import params
from .. import Plugin
from rocrate import rocrate_api
from rocrate.model.person import Person
from workflowhub.constants import WORKFLOWHUB_API_TOKEN

class CWL:
    version = 'v1.1'
    label = ''
    doc = ''
    inputs = []
    outputs = []
    steps = []
    ontology_name = 'cryoem'
    ontology_url = 'http://scipion.i2pc.es/ontology/'
    ontology_dict = {'Acquisition': 'CRYOEM_0000004',
                     'AtomStruct': 'CRYOEM_0000005',
                     'Coordinate': 'CRYOEM_0000006',
                     'CTFModel': 'CRYOEM_0000007',
                     'DefocusGroup': 'CRYOEM_0000008',
                     'EMSet': 'CRYOEM_0000009',
                     'SetOfAtomStructs': 'CRYOEM_0000023',
                     'SetOfClasses': 'CRYOEM_0000024',
                     'SetOfClasses2D': 'CRYOEM_0000065',
                     'SetOfClasses3D': 'CRYOEM_0000066',
                     'SetOfClassesVol': 'CRYOEM_0000067',
                     'SetOfCoordinates': 'CRYOEM_0000025',
                     'SetOfCTF': 'CRYOEM_0000026',
                     'SetOfDefocusGroup': 'CRYOEM_0000027',
                     'SetOfFSCs': 'CRYOEM_0000028',
                     'SetOfImages': 'CRYOEM_0000029',
                     'SetOfImages2D': 'CRYOEM_0000068',
                     'SetOfAverages': 'CRYOEM_0000094',
                     'SetOfMicrographs': 'CRYOEM_0000095',
                     'SetOfMovies': 'CRYOEM_0000096',
                     'SetOfParticles': 'CRYOEM_0000097',
                     'Class2D': 'CRYOEM_0000104',
                     'Class3D': 'CRYOEM_0000105',
                     'SetOfMovieParticles': 'CRYOEM_0000106',
                     'SetOfImages3D': 'CRYOEM_0000069',
                     'SetOfVolumes': 'CRYOEM_0000098',
                     'ClassVol': 'CRYOEM_0000107',
                     'SetOfNormalModes': 'CRYOEM_0000030',
                     'SetOfSequences': 'CRYOEM_0000031',
                     'FSC': 'CRYOEM_0000010',
                     'Image': 'CRYOEM_0000011',
                     'Image2D': 'CRYOEM_0000032',
                     'Average': 'CRYOEM_0000070',
                     'Mask': 'CRYOEM_0000071',
                     'Micrograph': 'CRYOEM_0000072',
                     'Movie': 'CRYOEM_0000073',
                     'Particle': 'CRYOEM_0000074',
                     'MovieParticle': 'CRYOEM_0000099',
                     'Image3D': 'CRYOEM_0000033',
                     'Volume': 'CRYOEM_0000075',
                     'VolumeMask': 'CRYOEM_0000076',
                     'NormalMode': 'CRYOEM_0000012',
                     'Sequence': 'CRYOEM_0000013',
                     'Transform': 'CRYOEM_0000014'}

    def __init__(self):
        pass

    def set(self, key, value):
        if key == 'version':
            self.version = value
        if key == 'label':
            self.label = value
        elif key == 'doc':
            self.doc = value
        elif key == 'steps':
            self.steps = value

    def format_steps(self):
        """ Formats the workflow steps in a proper way to be CWL-valid """
        if len(self.steps.keys()) > 0:
            steps_formatted = {}
            for id, step in self.steps.items():
                steps_formatted[step['class']] = {'label': step['label'], 'doc': step['summary']}
                steps_formatted[step['class']]['run'] = {'class': 'CommandLineTool', 'baseCommand': []}
                steps_formatted[step['class']]['out'] = []

                if len(step['input']) > 0:
                    steps_formatted[step['class']]['in'] = {}
                    steps_formatted[step['class']]['run']['inputs'] = {}
                    for input in step['input']:
                        steps_formatted[step['class']]['in'][input['id']] = {'source': input['source']}
                        steps_formatted[step['class']]['run']['inputs'][input['id']] = {'type': 'File',
                                                                                        'format': self.ontology_name + ':' + self.ontology_dict[input['class']] if input['class'] in self.ontology_dict else 'unknown'}
                else:
                    steps_formatted[step['class']]['in'] = []
                    steps_formatted[step['class']]['run']['inputs'] = []

                if len(step['output']) > 0:
                    steps_formatted[step['class']]['run']['outputs'] = {}
                    for output in step['output']:
                        steps_formatted[step['class']]['out'].append(output['id'])
                        steps_formatted[step['class']]['run']['outputs'][output['id']] = {'type': 'File',
                                                                                          'format': self.ontology_name + ':' + self.ontology_dict[output['class']] if output['class'] in self.ontology_dict else 'unknown'}
                else:
                    steps_formatted[step['class']]['run']['outputs'] = []

            return steps_formatted
        else:
            return []

    def validate(self, path, filename):
        """ Checks if a CWL workflow it's correct (in terms of syntax) """
        cmd = 'cwltool --validate %s' % '/'.join((path, filename))
        output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        return True if 'is valid CWL' in str(output.stdout) else False

    def create(self, path, filename):
        """ Creates a CWL workflow and checks if it is a valid one """
        workflow_cwl = {'cwlVersion': self.version,
                        'class': 'Workflow',
                        'label': self.label,
                        'doc': self.doc,
                        'inputs': [],
                        'outputs': [],
                        'steps': self.format_steps(),
                        '$namespaces': {self.ontology_name: self.ontology_url}}

        with open('/'.join((path, filename)), 'w') as file:
            yaml.dump(workflow_cwl, file, sort_keys=False)

        cwl_valid = True if self.validate(path, filename) else False
        return cwl_valid

    def __str__(self):
        return '<CWL {} {} {} {} {} {} {}>'.format(self.version, self.label, self.doc, self.inputs, self.outputs,
                                                   self.steps, self.ontology_name + ':' + self.ontology_url)

class WorkflowHubDepositor(EMProtocol):
    """
    Deposits an entry in WorkflowHub.
    """
    _label = 'WorkflowHub deposition'

    OUTPUT_WORKFLOW_JSON = 'workflow.json'
    OUTPUT_WORKFLOW_CWL = 'workflow.cwl'
    OUTPUT_WORKFLOW_ROCRATE = 'workflow.crate.zip'

    def __init__(self, **kwargs):
        EMProtocol.__init__(self, **kwargs)

    # --------------- DEFINE param functions ---------------

    def _defineParams(self, form):
        form.addSection(label='Entry')
        form.addParam('new', params.BooleanParam, label='Is this a new submission?', default=True, help='Is this a new submission or do you want to create a new version of an existing entry?')
        form.addParam('workflowHubID', params.StringParam, label='WorkflowHub workflow ID', condition='not new', help='Provide the existing WorkflowHub workflow ID. That could be checked at the workflow URL (i.e. would be XXX for https://workflowhub.eu/workflows/XXX?version=3 )')
        form.addParam('teamID', params.StringParam, label='WorkflowHub Team ID', validators=[params.NonEmpty], help='The RO-Crate owner team ID')
        form.addParam('name', params.StringParam, label='RO-Crate title', validators=[params.NonEmpty], help='The RO-Crate title')
        form.addParam('description', params.StringParam, label='RO-Crate description', validators=[params.NonEmpty], help='The RO-Crate description')
        form.addParam('keywords', params.StringParam, label='RO-Crate keywords', validators=[params.NonEmpty], help='Comma-separated RO-Crate keywords describing the workflow topics (i.e: cryoem, spa, 3d refinement)')
        form.addParam('publisher', params.StringParam, label='Entry publisher', validators=[params.NonEmpty], help='RO-Crate publisher (i.e: John Doe)')
        form.addParam('authorship', params.StringParam, label='Entry author/s (apart from publisher)', validators=[params.NonEmpty], help='Comma-separated workflow authors apart from the publisher one (i.e: Elisa Haley, Keith Winter)')

    # --------------- INSERT steps functions ----------------

    def _insertAllSteps(self):
        self._insertFunctionStep('makeDepositionStep')

    # --------------- STEPS functions -----------------------

    def makeDepositionStep(self):

        rocrate_valid = self.createROCrate()
        if rocrate_valid:
            payload = {'ro_crate': (self._getExtraPath(self.OUTPUT_WORKFLOW_ROCRATE),
                                    open(self._getExtraPath(self.OUTPUT_WORKFLOW_ROCRATE), 'rb')),
                       'workflow[project_ids][]': (None, self.teamID.get())}
            headers = {'authorization': 'Token %s' % os.environ[WORKFLOWHUB_API_TOKEN]}

            response = requests.post('https://workflowhub.eu/workflows/%s/create_version' % self.workflowHubID.get() if not self.new else 'https://workflowhub.eu/workflows', files=payload, headers=headers)

            if response.status_code in (200, 201):
                response = json.loads(response.text)
                latestVersion = int(response['data']['attributes']['latest_version'])
                workflowHubUrl = response['data']['attributes']['versions'][latestVersion - 1]['url']
                print("Workflow URL:", workflowHubUrl)
            else:
                print("There was an error when submitting to WorkflowHub: %s" % response.text)

    # --------------- INFO functions -------------------------

    def _validate(self):
        errors = []
        if not find_executable("dot"):
            errors.append("The Graphviz tool is not installed and the WorkflowHub entry will not have a proper diagram.")
        if WORKFLOWHUB_API_TOKEN not in os.environ:
            errors.append("Environment variable %s not set." % WORKFLOWHUB_API_TOKEN)
        if errors:
            errors.append("Please review the setup section at %s ." % Plugin.getUrl())

        return errors

    def _citations(self):
        return ['de_geest_paul_2021_5731379']

    def _summary(self):
        return []

    def _methods(self):
        return []

    # -------------------- UTILS functions -------------------------

    def createROCrate(self):
        """ Creates a RO-Crate zip with CWL workflow description, a diagram and other relevant metadata """

        # First, let's create the dependencies workflow
        project = self.getProject()
        workflowProts = [p for p in project.getRuns()]
        workflow = {}
        for prot in workflowProts:
            protDict = prot.getDefinitionDict()
            workflow[protDict['object.id']] = {'class': protDict['object.id'] + '_' + protDict['object.className'],
                                               'label': protDict['object.label'],
                                               'summary': ', '.join(map(str, prot.summary())),
                                               'input': [],
                                               'output': []}
            for a, input in prot.iterInputAttributes():
                workflow[protDict['object.id']]['input'].append(
                    {'id': input.getUniqueId().rsplit('.', 1)[0] if input.isPointer() else input.getObjName(),
                     'class': input.get().getClassName() if input.isPointer() else input.getClassName()})

            for a, output in prot.iterOutputAttributes():
                workflow[protDict['object.id']]['output'].append({'id': output.getObjName(),
                                                                  'class': output.getClassName()})

        # Relate inputs and outputs
        for id, prot in workflow.items():
            for input in prot['input']:
                for id, prot in workflow.items():
                    for output in prot['output']:
                        if input['id'] == output['id']:
                            input['source'] = prot['class'] + '/' + input['id']

        # Create a CWL workflow and if its syntax is ok then create the RO-Crate
        cwl = CWL()
        cwl.set('label', self.name.get())
        cwl.set('doc', self.description.get())
        cwl.set('steps', workflow)
        print("Saving CWL...")
        cwl_valid = cwl.create(self._getTmpPath(), self.OUTPUT_WORKFLOW_CWL)

        if cwl_valid:
            print("... CWL valid. Creating RO-Crate...")
            wf_path = self._getTmpPath(self.OUTPUT_WORKFLOW_CWL)
            wf_crate = rocrate_api.make_workflow_rocrate(workflow_path=wf_path, wf_type='CWL')

            # Data entities
            # workflow.json
            jsonStr = project.getProtocolsJson()
            f = open(self._getTmpPath(self.OUTPUT_WORKFLOW_JSON), 'w')
            f.write(jsonStr)
            f.close()
            wf_crate.add_file(self._getTmpPath(self.OUTPUT_WORKFLOW_JSON))

            # Contextual entities
            publisher = Person(wf_crate, properties={'name': self.publisher.get()})
            wf_crate.add(publisher)
            wf_crate.publisher = publisher
            creators = [publisher]
            for author in self.authorship.get().split(','):
                creator = Person(wf_crate, properties={'name': author})
                wf_crate.add(creator)
                creators.append(creator)
            wf_crate.creator = creators

            # Other metadata
            # create workflow diagram (dot tool from Graphviz must be installed)
            diagram_path = wf_path.replace('.cwl', '.svg')
            cmd = 'cwltool --print-dot %s | dot -Tsvg > %s' % (wf_path, diagram_path)
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            if os.path.exists(diagram_path):  # if the diagram was properly created
                wf_crate.add_file(diagram_path)
                wf_crate.image
                image = self.OUTPUT_WORKFLOW_CWL.replace('.cwl', '.svg')
                wf_crate.image = image

            wf_crate.license = 'Apache-2.0'
            wf_crate.name = self.name.get()
            wf_crate.description = self.description.get() + '\r\n\r\n In order to reproduce this workflow install Scipion software (http://scipion.i2pc.es/) and import the workflow.json file'
            wf_crate.keywords = [keyword.strip() for keyword in self.keywords.get().split(',')]

            rocrate_path = self._getExtraPath(self.OUTPUT_WORKFLOW_ROCRATE)
            wf_crate.write_zip(rocrate_path)
            print("... RO-Crate created")
        else:
            print("... CWL not valid. It is not possible to create RO-Crate")
        return cwl_valid