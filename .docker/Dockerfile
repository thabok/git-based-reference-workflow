# Starting from public image mathworks/matlab & btces/ep
# with default versions definde below (can be overwritten during build)
ARG EP_RELEASE=24.3p0
ARG MATLAB_RELEASE=R2024b

# FROM btces/ep:${EP_RELEASE} AS ep
FROM btces/ep:${EP_RELEASE} AS ep
FROM mathworks/matlab:${MATLAB_RELEASE} AS matlab

# ----------------------------------------------------------------------------------------
# MATLAB-specific configurations
# ----------------------------------------------------------------------------------------
# Install required matlab products & set up license
ARG MATLAB_RELEASE
ARG MATLAB_PRODUCTS="Embedded_Coder AUTOSAR_Blockset MATLAB_Coder Simulink Simulink_Coder Simulink_Coverage Stateflow"
ENV MLM_LICENSE_FILE=27000@matlab.license.server
USER root
RUN apt update && apt-get install -y wget
RUN wget -q https://www.mathworks.com/mpm/glnxa64/mpm && chmod +x mpm \
    && ./mpm install \
    --release=${MATLAB_RELEASE}  \
    --destination=/opt/matlab  \
    --products ${MATLAB_PRODUCTS} \
    && rm -f mpm /tmp/mathworks_root.log \
    && ln -f -s /opt/matlab/bin/matlab /usr/local/bin/matlab


# ----------------------------------------------------------------------------------------
# BTC-specific configurations
# ----------------------------------------------------------------------------------------
ENV LICENSE_LOCATION=27000@btc.license.server
# Copy files from public image btces/ep
COPY --chown=1000 --from=ep /opt /opt
COPY --chown=1000 --from=ep /root/.BTC /root/.BTC
# integrate BTC with MATLAB
RUN sudo chmod +x /tmp/addMLIntegration.bash && sudo /tmp/addMLIntegration.bash && sudo rm /tmp/addMLIntegration.bash
# install python module btc_embedded
RUN pip3 install --no-cache-dir btc_embedded

USER matlab
# Override default MATLAB entrypoint
ENTRYPOINT [  ]
CMD [ "python3", "-u", "scripts/run_tests.py" ]
