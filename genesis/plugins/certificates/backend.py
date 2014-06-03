import ConfigParser
import glob
import hashlib
import OpenSSL
import os

from genesis import apis
from genesis.com import *
from genesis.utils import SystemTime
from genesis.utils.error import SystemTimeError
from genesis.plugins.core.api import ISSLPlugin
from genesis.plugins.webapps.backend import WebappControl


class CertControl(Plugin):
	text = "Certificates"
	iconfont = 'gen-certificate'

	def get_certs(self):
		# Find all certs added by Genesis and return basic information
		certs, assigns = [], {}
		if not os.path.exists('/etc/ssl/certs/genesis'):
			os.mkdir('/etc/ssl/certs/genesis')
		if not os.path.exists('/etc/ssl/private/genesis'):
			os.mkdir('/etc/ssl/private/genesis')
		for x in glob.glob('/etc/nginx/sites-available/.*.ginf'):
			cfg = ConfigParser.ConfigParser()
			cfg.read(x)
			ssl = cfg.get('website', 'ssl', '')
			if ssl and assigns.has_key(ssl):
				assigns[ssl].append({'type': 'website', 'name': cfg.get('website', 'name')})
			elif ssl:
				assigns[ssl] = [{'type': 'website', 'name': cfg.get('website', 'name')}]
		for x in self.app.grab_plugins(ISSLPlugin):
			if self.app.gconfig.has_option('ssl_'+x.pid, 'cert'):
				ssl = self.app.gconfig.get('ssl_'+x.pid, 'cert')
				if ssl and assigns.has_key(ssl):
					assigns[ssl].append({'type': 'plugin', 'name': x.text, 'id': x.pid})
				elif ssl:
					assigns[ssl] = [{'type': 'plugin', 'name': x.text, 'id': x.pid}]
		if self.app.gconfig.set('genesis', 'ssl', '0') == '1':
			ssl = os.path.splitext(os.path.basename(self.app.gconfig.set('genesis', 'cert_file', '')))[0]
			if ssl and assigns.has_key(ssl):
				assigns[ssl].append({'type': 'genesis'})
			elif ssl:
				assigns[ssl] = [{'type': 'genesis'}]
		for x in glob.glob('/etc/ssl/certs/genesis/*.crt'):
			h, m = hashlib.sha1(), hashlib.md5()
			name = os.path.splitext(os.path.basename(x))[0]
			c = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(x, 'r').read())
			k = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(os.path.join('/etc/ssl/private/genesis', name+'.key'), 'r').read())
			h.update(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, c))
			m.update(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, c))
			h, m = h.hexdigest(), m.hexdigest()
			certs.append({'name': name,
				'expiry': c.get_notAfter(),
				'domain': c.get_subject().CN,
				'keytype': 'RSA' if k.type() == OpenSSL.crypto.TYPE_RSA else ('DSA' if k.type() == OpenSSL.crypto.TYPE_DSA else 'Unknown'),
				'keylength': str(int(k.bits())),
				'sha1': ':'.join([h[i:i+2].upper() for i in range(0,len(h), 2)]),
				'md5': ':'.join([m[i:i+2].upper() for i in range(0,len(m), 2)]),
				'assign': assigns[name] if assigns.has_key(name) else []})
		return certs

	def get_cas(self):
		# Find all certificate authorities generated by Genesis 
		# and return basic information
		certs = []
		if not os.path.exists('/etc/ssl/certs/genesis/ca'):
			os.mkdir('/etc/ssl/certs/genesis/ca')
		if not os.path.exists('/etc/ssl/private/genesis/ca'):
			os.mkdir('/etc/ssl/private/genesis/ca')
		for x in glob.glob('/etc/ssl/certs/genesis/ca/*.pem'):
			name = os.path.splitext(os.path.split(x)[1])[0]
			cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(x, 'r').read())
			key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, 
				open(os.path.join('/etc/ssl/private/genesis/ca', name+'.key'), 'r').read())
			certs.append({'name': name, 'expiry': cert.get_notAfter()})
		return certs

	def get_ssl_capable(self):
		lst = []
		for x in apis.webapps(self.app).get_sites():
			if x.ssl_able:
				lst.append(x)
		return lst, self.app.grab_plugins(ISSLPlugin)

	def has_expired(self, certname):
		# Return True if the plugin is expired, False if not
		c = open('/etc/ssl/certs/genesis/'+certname+'.crt', 'r').read()
		crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, c)
		return crt.has_expired()

	def add_ext_cert(self, name, cert, key, chain='', assign=[]):
		# Save the file streams as we get them, and
		# Add a .gcinfo file for a certificate uploaded externally
		try:
			crt = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
		except Exception, e:
			raise Exception('Could not read certificate file. Please make sure you\'ve selected the proper file.', e)
		try:
			ky = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
		except Exception, e:
			raise Exception('Could not read private keyfile. Please make sure you\'ve selected the proper file.', e)
		
		x = open(os.path.join('/etc/ssl/certs/genesis', name + '.crt'), 'w')
		x.write(cert)
		if chain:
			x.write('\n') if not cert.endswith('\n') else None
			x.write(chain)
		x.close()
		open(os.path.join('/etc/ssl/private/genesis', name + '.key'), 'w').write(key)

		if ky.type() == OpenSSL.crypto.TYPE_RSA:
			keytype = 'RSA'
		elif ky.type() == OpenSSL.crypto.TYPE_DSA:
			keytype = 'DSA'
		else:
			keytype = 'Unknown'
		os.chmod(os.path.join('/etc/ssl/certs/genesis', name + '.crt'), 0660)
		os.chmod(os.path.join('/etc/ssl/private/genesis', name + '.key'), 0660)

	def gencert(self, name, vars, hostname):
		# Make sure our folders are in place
		if not os.path.exists('/etc/ssl/certs/genesis'):
			os.mkdir('/etc/ssl/certs/genesis')
		if not os.path.exists('/etc/ssl/private/genesis'):
			os.mkdir('/etc/ssl/private/genesis')

		# If system time is way off, raise an error
		try:
			st = SystemTime().get_offset()
			if st < -3600 or st > 3600:
				raise SystemTimeError(st)
		except:
			raise SystemTimeError('UNKNOWN')

		# Check to see that we have a CA ready
		ca_cert_path = '/etc/ssl/certs/genesis/ca/'+hostname+'.pem'
		ca_key_path = '/etc/ssl/private/genesis/ca/'+hostname+'.key'
		if not os.path.exists(ca_cert_path) and not os.path.exists(ca_key_path):
			self.create_authority(hostname)
		ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(ca_cert_path).read())
		ca_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, open(ca_key_path).read())

		# Generate a key, then use it to sign a new cert
		# We'll use 2048-bit RSA until pyOpenSSL supports ECC
		keytype = OpenSSL.crypto.TYPE_DSA if self.app.get_config(self).keytype == 'DSA' else OpenSSL.crypto.TYPE_RSA
		keylength = int(self.app.get_config(self).keylength)
		try:
			key = OpenSSL.crypto.PKey()
			key.generate_key(keytype, keylength)
			crt = OpenSSL.crypto.X509()
			crt.set_version(3)
			if vars.getvalue('certcountry', ''):
				crt.get_subject().C = vars.getvalue('certcountry')
			if vars.getvalue('certsp', ''):
				crt.get_subject().ST = vars.getvalue('certsp')
			if vars.getvalue('certlocale', ''):
				crt.get_subject().L = vars.getvalue('certlocale')
			if vars.getvalue('certcn', ''):
				crt.get_subject().CN = vars.getvalue('certcn')
			if vars.getvalue('certemail', ''):
				crt.get_subject().emailAddress = vars.getvalue('certemail')
			crt.set_serial_number(int(SystemTime().get_serial_time()))
			crt.gmtime_adj_notBefore(0)
			crt.gmtime_adj_notAfter(2*365*24*60*60)
			crt.set_issuer(ca_cert.get_subject())
			crt.set_pubkey(key)
			crt.sign(ca_key, 'sha1')
		except Exception, e:
			raise Exception('Error generating self-signed certificate: '+str(e))
		open('/etc/ssl/certs/genesis/'+name+'.crt', "wt").write(
			OpenSSL.crypto.dump_certificate(
				OpenSSL.crypto.FILETYPE_PEM, crt)
			)
		os.chmod('/etc/ssl/certs/genesis/'+name+'.crt', 0660)
		open('/etc/ssl/private/genesis/'+name+'.key', "wt").write(
			OpenSSL.crypto.dump_privatekey(
				OpenSSL.crypto.FILETYPE_PEM, key)
			)
		os.chmod('/etc/ssl/private/genesis/'+name+'.key', 0660)

		if key.type() == OpenSSL.crypto.TYPE_RSA:
			keytype = 'RSA'
		elif key.type() == OpenSSL.crypto.TYPE_DSA:
			keytype = 'DSA'
		else:
			keytype = 'Unknown'

	def create_authority(self, hostname):
		key = OpenSSL.crypto.PKey()
		key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

		ca = OpenSSL.crypto.X509()
		ca.set_version(3)
		ca.set_serial_number(int(SystemTime().get_serial_time()))
		ca.get_subject().CN = hostname
		ca.gmtime_adj_notBefore(0)
		ca.gmtime_adj_notAfter(5*365*24*60*60)
		ca.set_issuer(ca.get_subject())
		ca.set_pubkey(key)
		ca.add_extensions([
		  OpenSSL.crypto.X509Extension("basicConstraints", True,
		                               "CA:TRUE, pathlen:0"),
		  OpenSSL.crypto.X509Extension("keyUsage", True,
		                               "keyCertSign, cRLSign"),
		  OpenSSL.crypto.X509Extension("subjectKeyIdentifier", False, "hash",
		                               subject=ca),
		  ])
		ca.sign(key, 'sha1')
		open('/etc/ssl/certs/genesis/ca/'+hostname+'.pem', "wt").write(
			OpenSSL.crypto.dump_certificate(
				OpenSSL.crypto.FILETYPE_PEM, ca)
			)
		os.chmod('/etc/ssl/certs/genesis/ca/'+hostname+'.pem', 0660)
		open('/etc/ssl/private/genesis/ca/'+hostname+'.key', "wt").write(
			OpenSSL.crypto.dump_privatekey(
				OpenSSL.crypto.FILETYPE_PEM, key)
			)

	def delete_authority(self, data):
		os.unlink(os.path.join('/etc/ssl/certs/genesis/ca', data['name']+'.pem'))
		os.unlink(os.path.join('/etc/ssl/private/genesis/ca', data['name']+'.key'))

	def assign(self, name, assign):
		# Assign a certificate to plugins/webapps as listed
		for x in assign:
			if x[0] == 'genesis':
				self.app.gconfig.set('genesis', 'cert_file', 
					'/etc/ssl/certs/genesis/'+name+'.crt')
				self.app.gconfig.set('genesis', 'cert_key', 
					'/etc/ssl/private/genesis/'+name+'.key')
				self.app.gconfig.set('genesis', 'ssl', '1')
				self.app.gconfig.save()
			elif x[0] == 'website':
				WebappControl(self.app).ssl_enable(x[1], name, 
					'/etc/ssl/certs/genesis/'+name+'.crt',
					'/etc/ssl/private/genesis/'+name+'.key')
				WebappControl(self.app).nginx_reload()
			elif x[0] == 'plugin':
				self.app.gconfig.set('ssl_'+x[1].pid, 'cert', name)
				self.app.gconfig.save()
				x[1].enable_ssl('/etc/ssl/certs/genesis/'+name+'.crt',
					'/etc/ssl/private/genesis/'+name+'.key')

	def unassign(self, assign):
		if assign[0] == 'genesis':
			self.app.gconfig.set('genesis', 'cert_file', '')
			self.app.gconfig.set('genesis', 'cert_key', '')
			self.app.gconfig.set('genesis', 'ssl', '0')
			self.app.gconfig.save()
		elif assign[0] == 'website':
			WebappControl(self.app).ssl_disable(assign[1])
			WebappControl(self.app).nginx_reload()
		elif assign[0] == 'plugin':
			self.app.gconfig.set('ssl_'+assign[1].pid, 'cert', '')
			self.app.gconfig.save()
			assign[1].disable_ssl()

	def remove(self, cert):
		# Remove cert, key and control file for associated name
		wal, pal = self.get_ssl_capable()
		for y in cert['assign']:
			for x in wal:
				if y['type'] == 'website' and y['name'] == x.name:
					WebappControl(self.app).ssl_disable(x)
					WebappControl(self.app).nginx_reload()
					break
			for x in pal:
				if y['type'] == 'plugin' and y['id'] == x.pid:
					x.disable_ssl()
					break
			if y['type'] == 'genesis':
				self.app.gconfig.set('genesis', 'cert_file', '')
				self.app.gconfig.set('genesis', 'cert_key', '')
				self.app.gconfig.set('genesis', 'ssl', '0')
				self.app.gconfig.save()
		try:
			os.unlink('/etc/ssl/certs/genesis/'+cert['name']+'.crt')
		except:
			pass
		try:
			os.unlink('/etc/ssl/private/genesis/'+cert['name']+'.key')
		except:
			pass
