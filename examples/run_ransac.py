"""
=================
Run RANSAC
=================


In this example we show how to run the RANSAC of ``pyprep``.
"""

# Authors: Yorguin Mantilla <yjmantilla@gmail.com>
#
# License: MIT
# Based On: use_noisy_module.py

###############################################################################
# First we import what we need for this example.
import numpy as np
import mne
from scipy import signal as sx
import time as clk

from pyprep.find_noisy_channels import NoisyChannels

###############################################################################
# Now let's make some arbitrary MNE raw object for demonstration purposes.
# We will think of good channels as sine waves and bad channels correlated with
# each other as sawtooths. The idea is that the RANSAC is able to identify
# these channels. We will need to set a montage because the RANSAC needs to
# interpolate.

sfreq = 1000.0

montage = mne.channels.make_standard_montage("standard_1020")

ch_names = montage.ch_names

n_chans = len(ch_names)

info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=["eeg"] * n_chans)

time = np.arange(0, 60, 1.0 / sfreq)  # 60 seconds of recording
n_bad_chans = 3  # num_good_chans = n_chans - num_bad_chans

bad_channels = np.random.choice(np.arange(n_chans), n_bad_chans, replace=False)
bad_channels = [int(i) for i in bad_channels]
bad_ch_names = [ch_names[i] for i in bad_channels]
freq_good = 20
freq_bad = 20

X = [
    sx.sawtooth(2 * np.pi * freq_bad * time)
    if i in bad_channels
    else np.sin(2 * np.pi * freq_good * time)
    for i in range(n_chans)
]
X = 2e-5 * np.array(X) + 1e-5 * np.random.random(
    (n_chans, time.shape[0])
)  # Scale to EEG and add noise.

raw = mne.io.RawArray(X, info)

raw.set_montage(montage, verbose=False)


###############################################################################
# Assign the mne object to the :class:`NoisyChannels` class. The resulting object
# will be the place where all following methods are performed.

nd = NoisyChannels(raw)


###############################################################################
# Find all bad channels and print a summary
start_time = clk.time()
nd.find_bad_by_ransac()
print("--- %s seconds ---" % (clk.time() - start_time))

###############################################################################
# Now the bad channels are saved in `bads` and we can continue processing our
# `raw` object. For more information, we can access attributes of the ``nd``
# instance:

# Check channels that go bad together by correlation (RANSAC)
print(nd.bad_by_ransac)
assert set(bad_ch_names) == set(nd.bad_by_ransac)
