import os

demdir = "../data/DEM"

lt1 = os.path.join(demdir, "20160112_vv_iw2.lt")

def main():
    os.remove(lt1)

if __name__ == "__main__":
    main()