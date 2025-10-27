from event_to_string import event_to_string

class StateMachine:
    def __init__(self, start_state, rules):
        self.cur_state = start_state
        self.rules = rules
        self.cur_state.enter(('START', 0))

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        for check_event in self.rules[self.cur_state].keys():
            if check_event(state_event):
                self.next_state = self.rules[self.cur_state][check_event]
                self.cur_state.exit(state_event)
                self.next_state.enter(state_event)
                print(f'State Transition: {self.cur_state.__class__.__name__} =============={event_to_string(state_event)} =========> {self.next_state.__class__.__name__}')
                self.cur_state = self.next_state
                return
        print(f'Unhandled Event: {event_to_string(state_event)}')
