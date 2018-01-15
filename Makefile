CDIMAGE=cdimage.debian.org/cdimage/buster_di_alpha1/$(shell dpkg --print-architecture)/iso-cd/debian-buster-DI-alpha1-$(shell dpkg --print-architecture)-netinst.iso

stretch/preseed.cfg: preseed.py my_preseed.py files/*
	mkdir -p $(@D)
	python3 my_preseed.py > $@

.PHONY: check
check:
	yapf3 -d *.py
	python3 -m unittest

$(notdir $(CDIMAGE)):
	wget --no-verbose $(CDIMAGE)

disk.img: script.exp $(notdir $(CDIMAGE)) stretch/preseed.cfg
	qemu-img create $@ 80G
	expect script.exp $(notdir $(CDIMAGE))

.PHONY: installcheck
installcheck: disk.img
	qemu-system-$(shell arch) \
	  -machine accel=kvm:tcg \
	  -smp $(shell nproc) \
	  -drive file=disk.img,if=virtio \
	  -net nic,model=virtio \
