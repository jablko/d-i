include /usr/share/dpkg/architecture.mk
export DEB_HOST_GNU_CPU # bug #888964
CDIMAGE=cdimage.debian.org/cdimage/buster_di_alpha1/$(DEB_HOST_ARCH)/iso-cd/debian-buster-DI-alpha1-$(DEB_HOST_ARCH)-netinst.iso
EXPECT=downloads.sourceforge.net/project/expect/Expect/5.45.3/expect5.45.3.tar.gz

stretch/preseed.cfg: preseed.py my_preseed.py files/*
	mkdir --parents $(@D)
	python3 my_preseed.py > $@

.PHONY: check
check:
	yapf3 --diff *.py
	python3 -m unittest

$(notdir $(CDIMAGE)):
	wget --no-verbose $(CDIMAGE)

$(notdir $(EXPECT)):
	wget --no-verbose $(EXPECT)

expect5.45.3/Makefile: $(notdir $(EXPECT))
	tar --extract --file $(notdir $(EXPECT))
	cd $(@D) && ./configure

disk.img: installer.exp stretch/preseed.cfg $(notdir $(CDIMAGE)) expect5.45.3/Makefile
	$(MAKE) -C expect5.45.3
	qemu-img create $@ 80G
	LD_LIBRARY_PATH=expect5.45.3 \
	  expect5.45.3/expect installer.exp $(notdir $(CDIMAGE))

.PHONY: installcheck
installcheck: disk.img
	qemu-system-$(DEB_HOST_GNU_CPU) \
	  -machine accel=kvm:tcg \
	  -smp $(shell nproc) \
	  -drive file=disk.img,if=virtio \
	  -net nic,model=virtio \
	  -net user \
