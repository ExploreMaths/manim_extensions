nbcell 效果预览
===============

交互查询(长行,验证右侧阴影)
----------------------------

.. nbcell::
    :output: array([ 0.9397, -0.7497,  0.    ])

    molecule = GraphMolecule.molecule_from_file("examples/molecule_files/mol_files/dimethylpropane.mol")
    print(molecule.find_atom_position_by_index(1))

.. nbcell::
    :output: array([0.51935, 0.59615, 0.     ])

    print(molecule.find_bond_center_by_index(1))

CLI(console,多行输出顺序验证)
-----------------------------

.. nbcell::
    :language: console
    :prompt-in: "$"
    :output: Retrieved molecule data for ('acetone', 'morphine'). Saving file(s) to . folder.
        File ./acetone.sdf is ready!!
        File ./morphine.sdf is ready!!
        Finished

    python -m manim_extensions.chemistry.cli pubchem-molecule --name acetone --name morphine