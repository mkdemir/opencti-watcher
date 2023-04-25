import sys
sys.path.append('../')
from src.app.opencti import OpenCTI

if __name__ == '__main__':

    opencti = OpenCTI()
    opencti.check_connection()
