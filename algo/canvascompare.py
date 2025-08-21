# canvascompare.py: Class for posthoc analysis of the results of the essay grading.
#
# Note: This is note used in the algorithm proper but instead supports the Intemass
# canvas (see ../canvas/views.py).
#

import logging

logger = logging.getLogger(__name__)


class Canvascompare:
    drawoptspair = {}

    def comparelist(self, sturulelist, stdrulelist):
        correctlist = []
        for stdrule in stdrulelist:
            print "\n11sadasdasd1232134123412312312312-----------------"*12
            print "stdrule = ",stdrule
            try:
                stdlegend_s = stdrule[1].split(')')[1].split('[')[0].strip()
            except:
                stdlegend_s = stdrule[1]
            try:
                stdlegend_e = stdrule[3].split(')')[1].split('[')[0].strip()
            except:
                stdlegend_e = stdrule[3]
            for sturule in sturulelist:
                try:
                    stulegend_s = sturule[1].split(')')[1].split('[')[0].strip()
                except:
                    stulegend_s = sturule[1]
                try:
                    stulegend_e = sturule[3].split(')')[1].split('[')[0].strip()
                except:
                    stulegend_e = sturule[3]
                if sturule[2].strip() == stdrule[2].strip() and stdlegend_s in self.drawoptspair.get(stulegend_s,"") and stdlegend_e in self.drawoptspair.get(stulegend_e,""):
                    correctlist.append(stdrule[0])
        return set(correctlist)

    def comparecurvesimilarity(self, stddrawopts, studrawopts):
        for stuelename in studrawopts:
            self.drawoptspair[stuelename] = set()
            self.drawoptspair.get(stuelename,"").add(stuelename)
            studrawelem = studrawopts.get(stuelename,"")
            stutype = studrawelem['type']
            for stdelename in stddrawopts:
                stddrawelem = stddrawopts.get(stdelename,"")
                stdtype = stddrawelem['type']
                if stutype == 'dot' and stdtype == 'dot':
                    if (studrawelem['start_x'] - stddrawelem['start_x']) ** 2 + (studrawelem['start_x'] - stddrawelem['start_x']) ** 2 < 2:
                        try:
                            self.drawoptspair.get(stuelename).add(str(stdelename))
                        except:
                            pass
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
                    try:
                        self.drawoptspair[stuelename].add(str(stdelename))
                    except:
                        pass

    def mark(self, comparelist, stdpointlist):
        if not stdpointlist:
            return None
        for pointlist in stdpointlist:
            if comparelist == set(pointlist['Point']):
                return pointlist['Mark']
        return 0
