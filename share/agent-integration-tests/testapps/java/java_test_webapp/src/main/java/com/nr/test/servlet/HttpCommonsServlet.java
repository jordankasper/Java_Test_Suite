package com.nr.test.servlet;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpMethod;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.methods.PostMethod;
import org.apache.commons.httpclient.params.HttpMethodParams;

public class HttpCommonsServlet extends TestServlet {

    @Override
    protected void processRequest(HttpServletRequest req, HttpServletResponse resp) throws ServletException,
            IOException {

        conductHttpCommonsv3Request1();
        conductHttpCommonsv3Request2();
        conductHttpCommonsv3Request3();

        conductHttpCommonsv3RequestPost1();

        super.processRequest(req, resp);
    }

    private void conductHttpCommonsv3Request1() {
        callHttpCommonsv3Request("http://www.apache.org/dyn/");
    }

    private void conductHttpCommonsv3Request2() {
        callHttpCommonsv3Request("http://www.amazon.com/gp/goldbox");
    }

    private void conductHttpCommonsv3Request3() {
        callHttpCommonsv3Request("http://news.yahoo.com");
    }

    private void conductHttpCommonsv3RequestPost1() {
        callHttpCommonsv3RequestPost("http://search.yahoo.com/search");
    }

    private void callHttpCommonsv3Request(String path) {
        try {
            HttpClient httpClient = new HttpClient();
            HttpMethod method = new GetMethod(path);
            httpClient.executeMethod(method);
            method.releaseConnection();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void callHttpCommonsv3RequestPost(String path) {
        try {
            HttpClient httpClient = new HttpClient();
            HttpMethod method = new PostMethod(path);
            HttpMethodParams params = new HttpMethodParams();
            params.setBooleanParameter("testing", true);
            method.setParams(params);

            httpClient.executeMethod(method);
            method.releaseConnection();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public String getServletInfo() {
        return "external call http commons servlet";
    }
}
