##
#    Copyright (c) 2007 Cyrus Daboo. All rights reserved.
#    
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    
#        http://www.apache.org/licenses/LICENSE-2.0
#    
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##

from datetime import PyCalendarDateTime

class PyCalendarComponentExpanded(object):

    @staticmethod
    def sort_by_dtstart_allday(e1, e2):

        if e1.mInstanceStart.isDateOnly() and e2.mInstanceStart.isDateOnly():
            return e1.mInstanceStart.lt(e2.mInstanceStart)
        elif e1.mInstanceStart.isDateOnly():
            return True;
        elif e2.mInstanceStart.isDateOnly():
            return False;
        elif e1.mInstanceStart.eq(e2.mInstanceStart):
            if e1.mInstanceEnd.eq(e2.mInstanceEnd):
                # Put ones created earlier in earlier columns in day view
                return e1.getOwner().getStamp().lt(e2.getOwner().getStamp())
            else:
                # Put ones that end later in earlier columns in day view
                return e1.mInstanceEnd.gt(e2.mInstanceEnd)
        else:
            return e1.mInstanceStart.lt(e2.mInstanceStart)

    @staticmethod
    def sort_by_dtstart(e1, e2):
        if e1.mInstanceStart.eq(e2.mInstanceStart):
            if (e1.mInstanceStart.isDateOnly() and not e2.mInstanceStart.isDateOnly() or
                not e1.mInstanceStart.isDateOnly() and e2.mInstanceStart.isDateOnly()):
                return e1.mInstanceStart.isDateOnly()
            else:
                return False
        else:
            return e1.mInstanceStart.lt(e2.mInstanceStart)

    def __init__(self, owner=None, rid=None, copyit=None):

        if owner is not None:
            self.mOwner = owner
            self.initFromOwner(rid)
        elif copyit is not None:
            self._copy_PyCalendarComponentExpanded(copyit)

    def close(self):
        # Clean-up
        self.mOwner = None;

    def getOwner(self):
        return self.mOwner

    def getMaster(self):
        return self.mOwner

    def getTrueMaster(self):
        return self.mOwner.getMaster()

    def getInstanceStart(self):
        return self.mInstanceStart

    def getInstanceEnd(self):
        return self.mInstanceEnd

    def recurring(self):
        return self.mRecurring

    def isNow(self):
        # Check instance start/end against current date-time
        now = PyCalendarDateTime.getNowUTC()
        return self.mInstanceStart.le(now) and self.mInstanceEnd.gt(now)

    def initFromOwner(self, rid):
        # There are four possibilities here:
        #
        # 1: this instance is the instance for the master component
        #
        # 2: this instance is an expanded instance derived directly from the
        # master component
        #
        # 3: This instance is the instance for a slave (overridden recurrence
        # instance)
        #
        # 4: This instance is the expanded instance for a slave with a RANGE
        # parameter
        #

        # rid is not set if the owner is the master (case 1)
        if rid is None:
            # Just get start/end from owner
            self.mInstanceStart = self.mOwner.getStart()
            self.mInstanceEnd = self.mOwner.getEnd()
            self.mRecurring = False

        # If the owner is not a recurrence instance then it is case 2
        elif not self.mOwner.isRecurrenceInstance():
            # Derive start/end from rid and duration of master

            # Start of the recurrence instance is the recurrence id
            self.mInstanceStart = rid

            # End is based on original events settings
            if self.mOwner.hasEnd():
                self.mInstanceEnd = self.mInstanceStart.add(self.mOwner.getEnd().subtract(self.mOwner.getStart()))
            else:
                self.mInstanceEnd = PyCalendarDateTime(copyit=self.mInstanceStart)

            self.mRecurring = True

        # If the owner is a recurrence item and the passed in rid is the same
        # as the component rid we have case 3
        elif rid.eq(self.mOwner.getRecurrenceID()):
            # Derive start/end directly from the owner
            self.mInstanceStart = self.mOwner.getStart()
            self.mInstanceEnd = self.mOwner.getEnd()

            self.mRecurring = True

        # case 4 - the complicated one!
        else:
            # We need to use the rid as the starting point, but adjust it by
            # the offset between the slave's
            # rid and its start
            self.mInstanceStart = rid.add(self.mOwner.getStart().subtract(self.mOwner.getRecurrenceID()))

            # End is based on duration of owner
            self.mInstanceEnd = self.mInstanceStart.add(self.mOwner.getEnd().subtract(self.mOwner.getStart()))

            self.mRecurring = True

    def _copy_ICalendarComponentExpanded(self, copy):
        self.mOwner = copy.self.mOwner
        self.mInstanceStart = PyCalendarDateTime(copy.mInstanceStart)
        self.mInstanceEnd = PyCalendarDateTime(copy.mInstanceEnd)
        self.mRecurring = copy.mRecurring
