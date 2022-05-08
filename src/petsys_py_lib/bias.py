from . import spi
from math import ceil

def read_febd_bias_info(conn, portID, slaveID):

	n_slots = conn.read_config_register(portID, slaveID, 8, 0x0030)
	bias_type_info = conn.read_config_register(portID, slaveID, 16, 0x0031)

	result = {}
	for n in range(n_slots):
		bias_type = (bias_type_info >> (4*n)) & 0xF
		if bias_type == 0xF:
			result[n] = (False, 64, "ad5535rev1", False)

		elif bias_type == 0xE:
			result[n] = (True, 16, "ltc2668rev1", True)

	return result




def set_channel(conn, key, value):
	print("DEBUG", key, value)
	portID, slaveID, slotID, channelID = key
	bias_info = conn.getUnitInfo(portID, slaveID)["bias"]

	_, _, bias_type, _ = bias_info[slotID]

	if bias_type == "ad5535rev1":
		if channelID > 32:
			chipID = 0x8000 + 0x100 * slotID + 0x11
		else:
			chipID = 0x8000 + 0x100 * slotID + 0x10
		channelID = channelID % 32

		# Impose minimum 1V bias voltage
		min_dac = int(ceil(2**14 * 1.0 / 200))
		value = max(value, min_dac)

		spi.ad5535_set_channel(conn, portID, slaveID, chipID, channelID, value)

	elif bias_type == "ltc2668rev1":
		# Impose minimum 1V bias voltage
		min_dac = int(ceil(2**16 * 1.0 / 75))
		value = max(value, min_dac)
	
		chipID = 0x8000 + 0x100 * slotID + 0x10
		spi.ltc2668_set_channel(conn, portID, slaveID, chipID, channelID, value)

	return None


def get_active_channels(conn):
	r = []
	for p, s in conn.getActiveFEBDs():
		bias_info = conn.getUnitInfo(p, s)["bias"]
		for n, (has_prom, n_channels, bias_type, has_adc) in bias_info.items():
			r += [ (p, s, n, k) for k in range(n_channels) ]

	return r





	

