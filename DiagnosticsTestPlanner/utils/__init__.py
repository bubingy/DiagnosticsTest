import os
os.environ['planner_root'] = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
os.environ['planner_conf_dir'] = os.path.join(
    os.environ['planner_root'], 'conf'
)