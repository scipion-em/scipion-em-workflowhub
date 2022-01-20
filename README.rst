=============================
Scipion WorkflowHub Depositor
=============================

This **Scipion** plugin allows to upload Workflow RO-Crates (https://w3id.org/ro/crate) to WorkflowHub (https://workflowhub.eu/) with the aim of allowing other scientist to use your template in their analysis.

=====
Setup
=====

You will need to use `Scipion3 <https://scipion-em.github.io/docs/docs/scipion
-modes/how-to-install.html>`_ to run these protocols.

1. **Install the plugin:**

- **Install the stable version (Not available yet)**

    Through the **plugin manager GUI** by launching Scipion and following **Configuration** >> **Plugins** or

.. code-block::

    scipion installp -p scipion-em-workflowhub


- **Developer's version**

    1. Download repository:

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-workflowhub.git

    2. Install:

    .. code-block::

        scipion3 installp -p path_to_scipion-em-workflowhub --devel

2.  Open scipion's config file 'scipion3 config --show' and add your WorkflowHub API Token :

.. code-block::

    WORKFLOWHUB_API_TOKEN = <workflowhub_api_token>

NOTE: If you want to create a diagram that illustrates the workflow you must have Graphviz installed (https://graphviz.org/download/)