from BaseResponse import BaseResponse

class SimpleResponse(BaseResponse):
    def react(self, *args):
        self.respond(*args)
