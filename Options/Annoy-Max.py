import pulsectl

# Create a PulseAudio controller
with pulsectl.Pulse('volume-control') as pulse:
    # Get all sinks (output devices)
    sinks = pulse.sink_list()
    if sinks:
        # Set the volume to maximum (1.0) for the first sink
        pulse.volume_set_all_chans(sinks[0], 1.0)
    else:
        print("No sinks found")
