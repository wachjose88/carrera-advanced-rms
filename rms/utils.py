import locale


def formattime(time, longfmt=True):
    if time is None:
        return 'n/a'
    s = int(time // 1000)
    ms = int(time % 1000)

    if not longfmt:
        sms = float(str(s)+'.'+str('%03d' % (ms)))
        return locale.format_string('%.3f', sms)
    elif s < 3600:
        sms = float(str(s % 60) + '.' + str('%03d' % (ms)))
        t = '%d:' % (s // 60)
        return t + locale.format_string('%06.3f', sms)
    else:
        sms = float(str(s % 60) + '.' + str('%03d' % (ms)))
        t = '%d:%02d:' % (s // 3600, (s // 60) % 60)
        return t + locale.format_string('%06.3f', sms)
