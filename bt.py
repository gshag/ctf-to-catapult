import sys
import bt2
import json

def event_to_catapult(msg):
  out = {}
  ev = msg.event
  # Record the timestamp
  out['ts'] = "{}.{:03d}".format(msg.default_clock_snapshot.ns_from_origin // 1000, msg.default_clock_snapshot.ns_from_origin % 1000)
  out['pid'] = int(ev.packet.context_field.get('pid'))
  out['tid'] = int(ev.specific_context_field.get('tid'))
  # Entry GC event
  if ev.id == 0:
    out['ph'] = 'B'
    out['name'] = str(ev['phase'].labels[0])
  # Exit GC event
  if ev.id == 1:
    out['ph'] = 'E'
    out['name'] = str(ev['phase'].labels[0])
  # Counter GC events
  if ev.id == 2:
    out['args'] = {'value': int(ev['count'])}
    out['name'] = str(ev['kind'].labels[0])
    out['ph'] = 'C'
  # Alloc GC events
  if ev.id == 3:
    out['args'] = {'value': int(ev['count'])}
    out['name'] = str(ev['bucket'].labels[0])
    out['ph'] = 'C'
  # Flush events
  if ev.id == 4:
   out['ph'] = 'X'
   out['name'] = 'eventlog/flush'
   out['dur'] = "{}.{:03d}".format(int(ev['duration']) // 1000, int(ev['duration']) % 1000)
  # User events
  if ev.id > 4:
  	out['name'] = ev.name
  	# Begin user event
  	if int(ev['span_type']) == 31:
  		out['ph'] = 'B'
  	# End user event
  	else:
  		out['ph'] = 'E'

  return out

def main():
  # Find the `ctf` plugin (shipped with Babeltrace 2).
	ctf_plugin = bt2.find_plugin('ctf')

	# Get the `source.ctf.fs` component class from the plugin.
	fs_cc = ctf_plugin.source_component_classes['fs']

	trace_dir = sys.argv[1]
	# Create a trace collection message iterator, instantiating a single
	# `source.ctf.fs` component class with the `inputs` initialization
	# parameter set to open a single CTF trace.
	msg_it = bt2.TraceCollectionMessageIterator(bt2.ComponentSpec(fs_cc, {
    'inputs': [trace_dir],
	}))

	catapult_objects = list()

	# Iterate over the trace messages.
	for msg in msg_it:
	  # `bt2._EventMessageConst` is the Python type of an event message.
	  if type(msg) is bt2._EventMessageConst:
	    # Convert the event to the catapult format.
	    catapult_objects.append(event_to_catapult(msg))

	catapult = {
    'displayTimeUnit': 'ns',
    'traceEvents': catapult_objects
  }
	
	with open(sys.argv[2], "w") as out:
		out.write(json.dumps(catapult))

if __name__ == '__main__':
  main()