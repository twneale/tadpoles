Presto account unlocker script
==============================

WHAT
++++

This script is an automated client for presto.private.massmutual.com. Internally the script uses headless a headless Firefox browser (via selenium and X virtual frame buffers!) to submit your info to the form, but you can build/run the program with only docker installed.

Dependencies
++++++++++++

Docker 

Usage
+++++

To use it, create a .presto.yml file in the same directory containing your mm id and your secret question answers (note: keep the file secret!). The file looks like this::

    ---
    mm_id: mm20698
    name of your best man: cow
    5th grade teacher: says
    favorite childhood friend: moo

The keys in the yaml map are lowercased strings that appear in your questions; the values are the answers. The config file is added to the container as a volume at runtime and is not copied into the image at build time. 

Build the docker images::

    $ ./build.sh.

Then run a presto container::

    $ ./run.sh    

Now your account should be unlocked.