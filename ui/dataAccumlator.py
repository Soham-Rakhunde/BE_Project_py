# used to accumlate data from host TLS interface objects

from utils.singleton_meta import SingletonMeta

class DataLogger(metaclass=SingletonMeta):
    headers = ["Thread Id", "Chunk Id", "Peer Id", "Peer IP Address", 'Location List', "Status"]
    valueList = dict()
    finalList = [[' ',' ',' ',' ',' ',' ']]

    commmonHeaders= ["File Name", "File Size(Bytes)", "Total Chunks", "Completed", 'Redundancy Ratio', "Required Peers"]
    commonInfoList = [[' ',0,0,0,0,0]]

    retrieverHeaders= ["File Name", "Total Chunks", "Completed", "Active Peers with Chunks", "Redundant Peers", "Unsuccesful attempts","Inactive Peers"]
    retrieverInfoList = [[' ',0,0,0,0, 0, 0]]

    def flush(self):
        self.valueList = dict()
        self.finalList = [[' ',' ',' ',' ',' ',' ']]
        self.commonInfoList = [[' ',' ',' ',' ',' ']]

    def write(self, threadID: str, chunkId: str, peer_id: str, peer_addr: str, locationList: list=None):
        loc = ", ".join(locationList) if locationList else "-"
        self.valueList[peer_id] = [threadID, chunkId, peer_id, peer_addr, loc, "Ongoing"]
        self.finalList = list(self.valueList.values())

    def update(self, peer_id, locationList: list = None, status: str = None):
        if locationList is not None:
            loc = ", ".join(locationList) if locationList else ""
            self.valueList[peer_id][4] = loc
            self.valueList[peer_id][5] = "Successful"
            self.finalList = list(self.valueList.values())
            return
        elif status is not None:
            self.valueList[peer_id][5] = status
            self.finalList = list(self.valueList.values())
            return
    
