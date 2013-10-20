from gi.repository import Gst, GstController
from gi.repository import GES
from gi.repository import GLib
from gi.repository import GObject
import sys

loop = GLib.MainLoop()

def get_source_by_type(clip, track_type):
    for source in clip.get_children(False): # don't recurse
        if source.get_track_type() == track_type and isinstance(source, GES.Source):
            return source

def mylog(x):
    return (x / (1 + x))

def do_nifty_mixing(timeline, video_asset, nbr):
    step = 1.0 / nbr
    alpha = step
    for i in range(nbr):
        layer = timeline.append_layer()
        video_clip = layer.add_asset(video_asset, 0, i * Gst.SECOND * 0.3, 60 * Gst.SECOND, GES.TrackType.VIDEO)

        source = get_source_by_type(video_clip, GES.TrackType.VIDEO)
        source.set_child_property("alpha", alpha)
        alpha += step

def add_question_image(asset, layer, start, duration):
    image_clip = layer.add_asset(asset, start, 0, duration, GES.TrackType.VIDEO)
    effect = GES.Effect.new("agingtv")
    image_clip.add(effect)

def add_decreasing_music(asset, layer):
    music_clip = layer.add_asset(asset, 0, 0, 60 * Gst.SECOND, GES.TrackType.AUDIO)
    element = get_source_by_type(music_clip, GES.TrackType.AUDIO)

    source = GstController.InterpolationControlSource()
    element.set_control_source(source, "volume", "direct")
    source.props.mode = GstController.InterpolationMode.LINEAR

    source.set(0, 0.1)
    source.set(50 * Gst.SECOND, 0.1)
    source.set(60 * Gst.SECOND, 0.0)

def do_some_awesome_edition(timeline):
    video_asset = GES.UriClipAsset.request_sync("file:///home/meh/Videos/dancer.mp4")
    audio_asset = GES.UriClipAsset.request_sync("file:///home/meh/Music/daso.mp3")
    image_asset = GES.UriClipAsset.request_sync("file:///home/meh/Pictures/questions.jpg")

    layer = timeline.append_layer()
    video_clip = layer.add_asset(video_asset, 0, 0, 5 * Gst.SECOND, GES.TrackType.VIDEO) # start, inpoint, duration, track type

    #source = get_source_by_type(video_clip, GES.TrackType.VIDEO)
    #source.set_child_property("alpha", 0.5)

    # do_nifty_mixing(timeline, video_asset, 4)
    # layer = timeline.append_layer()
    # add_decreasing_music(audio_asset, layer)
    # add_question_image(image_asset, layer, 60 * Gst.SECOND, audio_asset.get_duration() - video_asset.get_duration())

    timeline.commit()

def busMessageCb(unused_bus, message):
    global pipeline
    global loop
    if message.type == Gst.MessageType.EOS or message.type == Gst.MessageType.ERROR:
        print "Bye, got EOS"
        loop.quit()
        pipeline.set_state(Gst.State.NULL)

if __name__=="__main__":
    GObject.threads_init()
    Gst.init(None)
    GES.init()

    pipeline = GES.Pipeline()
    timeline = GES.Timeline.new_audio_video()

    do_some_awesome_edition(timeline)

    pipeline.add_timeline(timeline)
    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", busMessageCb)

    try:
        loop.run()
    except KeyboardInterrupt:
        sys.stdout.write('\b\b  \b\b')
        pipeline.set_state(Gst.State.NULL)
