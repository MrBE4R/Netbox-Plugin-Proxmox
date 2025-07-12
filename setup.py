from setuptools import find_packages, setup

setup(
    name="netbox-plugin-proxmox",
    version="2025.07.14",
    description="Plugins to automatically sync virtual machines from multiples proxmox cluster or instances",
    install_requires=["proxmoxer"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author="Jean-François GUILLAUME",
    author_email="jean-francois.guillaume@univ-nantes.fr",
)
