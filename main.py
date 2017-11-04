# OpenNero will execute ModMain when this mod is loaded
import OpenNero
import common

import TowerofHanoi.main
import TowerofHanoi.constants
from TowerofHanoi.module import getMod, TowerEnvironment
import Hw4.agent

def start_nlp_extended(): #Natural Language Processing
    """ start the tower demo """
    getMod().num_disks = 3
    OpenNero.disable_ai()
    getMod().stop_agent()
    env = TowerEnvironment()
    env.initialize_blocks()
    getMod().set_environment(env)
    getMod().agent_id = common.addObject("data/shapes/character/MyNLPRobot.xml", OpenNero.Vector3f(TowerofHanoi.constants.GRID_DX, TowerofHanoi.constants.GRID_DY, 2), type=TowerofHanoi.constants.AGENT_MASK, scale=OpenNero.Vector3f(3,3,3))
    OpenNero.enable_ai()

def ModMain():
    agent_desc = ('Extended Semantic Parser', start_nlp_extended, "")
    getMod().AGENTS.append(agent_desc)
    TowerofHanoi.main.ModMain()

