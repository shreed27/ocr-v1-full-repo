import logging

logger = logging.getLogger(__name__)


class Canvascompare:
    drawoptspair = {}

    def comparelist(self, sturulelist, stdrulelist):
        correctlist = []
        for stdrule in stdrulelist:
            stdlegend_s = stdrule[1].split(')')[1].split('[')[0].strip()
            stdlegend_e = stdrule[3].split(')')[1].split('[')[0].strip()
            for sturule in sturulelist:
                stulegend_s = sturule[1].split(')')[1].split('[')[0].strip()
                stulegend_e = sturule[3].split(')')[1].split('[')[0].strip()
                if sturule[2].strip() == stdrule[2].strip() and stdlegend_s in self.drawoptspair[stulegend_s] and stdlegend_e in self.drawoptspair[stulegend_e]:
                    correctlist.append(stdrule[0])
        return set(correctlist)

    def comparecurvesimilarity(self, stddrawopts, studrawopts):
        for stuelename in studrawopts:
            self.drawoptspair[stuelename] = set()
            self.drawoptspair[stuelename].add(stuelename)
            studrawelem = studrawopts[stuelename]
            stutype = studrawelem['type']
            for stdelename in stddrawopts:
                stddrawelem = stddrawopts[stdelename]
                stdtype = stddrawelem['type']
                if stutype == 'dot' and stdtype == 'dot':
                    if (studrawelem['start_x'] - stddrawelem['start_x']) ** 2 + (studrawelem['start_x'] - stddrawelem['start_x']) ** 2 < 2:
                        self.drawoptspair[stuelename].add(str(stdelename))
                elif stutype != 'dot' and stutype == stdtype:
                    simlen = len(studrawelem['rcoordinate']) if (len(studrawelem['rcoordinate']) < len(stddrawelem['rcoordinate'])) else len(stddrawelem['rcoordinate'])
                    sumofdistance = 0
                    for i in range(simlen):
                        stuvec = [studrawelem['rcoordinate'][i][0], studrawelem['rcoordinate'][i][1]]
                        stdvec = [stddrawelem['rcoordinate'][i][0], stddrawelem['rcoordinate'][i][1]]
                        distance = (stuvec[0] - stdvec[0]) ** 2 + (stuvec[1] - stdvec[1]) ** 2
                        sumofdistance += distance
                        if distance > 0.02 or sumofdistance > 0.05:
                            break
                    self.drawoptspair[stuelename].add(str(stdelename))

    def mark(self, comparelist, stdpointlist):
        if not stdpointlist:
            return None
        for pointlist in stdpointlist:
            if comparelist == set(pointlist['Point']):
                return pointlist['Mark']
        return 0
