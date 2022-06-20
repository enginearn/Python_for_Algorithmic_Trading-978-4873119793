FROM enginearn/ubuntu-latest-jp:latest

ADD install.sh /
RUN chmod u+x /install.sh
RUN /install.sh
ENV PATH $HOME/miniconda3/bin:$PATH

CMD ["su sudo_user && cd $HOME"]