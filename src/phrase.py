from talon import speech_system, Module

mod = Module()

class Phrase:
    stop_listening_callback = None

    def on_phrase(self, p: dict):
        if p.get("text"):
            text = None
            # text is a list, if the first word is prompt, then join all of the rest of the text together
            print(p.get("text"))
            if p.get("text")[0] == "prompt":
                text = " ".join(p.get("text")[1:])

            print(f"Phrase: {text}")
            # self.stop_listening()
            # if self.stop_listening_callback:
            #     self.stop_listening_callback()
            #     self.stop_listening_callback = None

    def stop_listening(self):
        speech_system.unregister("post:phrase", self.on_phrase)

    def start_listening(self):
        speech_system.register("post:phrase", self.on_phrase)

    def await_next_phrase(self, callback):
        if self.stop_listening_callback:
            self.stop_listening()
        self.stop_listening_callback = callback
        self.start_listening()

phrase = Phrase()

@mod.action_class
class Actions:
    def test_start_listening():
        """Start listening for a phrase"""
        phrase.start_listening()

    def test_stop_listening():
        """Stop listening for a phrase"""
        phrase.stop_listening()
